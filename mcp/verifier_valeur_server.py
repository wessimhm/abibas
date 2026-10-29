#!/usr/bin/env python3
"""
Serveur MCP « métier » d’Abibas : « verifier-valeur » (alias abibas-labo dans la formation).
Démo formation IA, vendredi 2 · Abibas Sport est fictif.

Cinq outils nommés, avec des requêtes fixées et testées. Le modèle ne voit jamais la base,
seulement ces outils :
- lister_exigences() : les critères de SPEC-LFB-BAL-01 rév. C ;
- lire_resultats(sn) : les résultats d'essai d'un spécimen (ex. L-0042) ;
- verifier_valeur(exigence, valeur_mesuree, unite) : « dans le critère » ou « hors critère », avec l'écart ;
- chercher_nc(mot_cle) : cherche dans le registre des non-conformités ;
- calculer_devis(essais, nb_specimens, delai_jours_ouvrables) : applique la grille tarifaire 2026.

Les données viennent de la base du labo donnees/abibas-labo.db (créée par outils/creer_base.py),
ouverte en lecture seule. Chaque appel ajoute une ligne à donnees/journal-mcp.log (traçabilité).
Le calcul est fait par du code, pas par le modèle : même entrée, même réponse.
Aucun outil ne prononce la conformité : c'est le rôle de l'ingénieure responsable.

Lancement : python3 mcp/verifier_valeur_server.py   (Claude le lance tout seul via .mcp.json)
Essai sans Claude : python3 mcp/verifier_valeur_server.py --test
Dépendance : pip install mcp (SDK officiel 1.x ou 2.x). Sans le SDK, les fonctions restent
importables et testables (import verifier_valeur_server).
"""
import datetime
import json
import os
import sqlite3
import sys
import unicodedata

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RACINE, "donnees", "abibas-labo.db")
JOURNAL = os.path.join(RACINE, "donnees", "journal-mcp.log")

ALIAS = {"EX-01": "EX-01-rebond", "EX-02": "EX-02-pression", "EX-03": "EX-03-prise-eau",
         "EX-04": "EX-04-rebond", "EX-05": "EX-05-perte",
         "EX-03-prise-d-eau": "EX-03-prise-eau", "EX-03-eau": "EX-03-prise-eau"}

# Écritures acceptées pour une même unité (le glossaire impose la valeur).
UNITES = {
    "cm": "cm", "centimètre": "cm", "centimetre": "cm", "centimètres": "cm", "centimetres": "cm",
    "m": "m", "mètre": "m", "metre": "m", "g": "g", "gramme": "g", "grammes": "g",
    "bar": "bar", "bars": "bar", "%": "%", "pourcent": "%", "pour cent": "%",
    "km/h": "km/h", "kmh": "km/h", "tir": "tirs", "tirs": "tirs", "position": "positions", "positions": "positions",
    "h": "h", "heure": "h", "heures": "h", "min": "min", "minute": "min", "minutes": "min",
    "°c": "°C", "c": "°C", "degc": "°C", "celsius": "°C", "cycle": "cycles", "cycles": "cycles",
}
FAHRENHEIT = {"°f", "f", "degf", "fahrenheit"}
ESSAIS = {"rebond": "rebond", "tirs": "tirs", "tirs repetes": "tirs", "tir": "tirs", "absorption": "absorption",
          "absorption d'eau": "absorption", "absorption d’eau": "absorption", "eau": "absorption",
          "froid": "froid", "usure": "usure", "abrasion": "usure"}


# ---------------------------------------------------------------- utilitaires
def _base():
    """Connexion en lecture seule à la base du labo."""
    if not os.path.exists(BASE):
        raise FileNotFoundError(f"base introuvable : {BASE} (lancer python3 outils/creer_base.py)")
    return sqlite3.connect(f"file:{BASE}?mode=ro", uri=True)


def _journal(outil, arguments, resultat):
    """Une ligne par appel : date, serveur, outil, arguments, résultat court. Silencieux si l'écriture échoue."""
    try:
        court = " ".join(str(resultat).split())[:140]
        with open(JOURNAL, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} | verifier-valeur | {outil} | "
                    f"{json.dumps(arguments, ensure_ascii=False)} | {court}\n")
    except Exception:
        pass


def _fmt(x):
    if x is None:
        return "—"
    if isinstance(x, float):
        t = f"{x:.2f}".rstrip("0")
        t = t + "0" if t.endswith(".") else t
    elif isinstance(x, int) and abs(x) >= 1000:
        t = f"{x:,}".replace(",", " ")
    else:
        t = str(x)
    return t.replace(".", ",").replace("-", "−")


def _sans_accent(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "")) if unicodedata.category(c) != "Mn").lower().strip()


def _unite(u):
    u = (u or "").strip()
    if u.lower() in FAHRENHEIT:
        return "°F"
    return UNITES.get(u.lower(), u)


def _dollars(x):
    return f"{x:,.0f}".replace(",", " ") + " $"


def _exigences():
    with _base() as cx:
        return {r[0]: {"essai": r[1], "parametre": r[2], "op": r[3], "critere": r[4], "unite": r[5], "rev": r[6]}
                for r in cx.execute("SELECT id, essai, parametre, operateur, valeur_critere, unite, revision "
                                    "FROM exigences ORDER BY rowid")}


COMPTES = {"cycles", "min", "positions", "tirs", "cm", "km/h"}  # unités sans décimale


def _num(x, unite):
    if unite in COMPTES and isinstance(x, float) and x.is_integer():
        x = int(x)
    return _fmt(x)


def _borne(e):
    signe = {">=": "≥", "<=": "≤", "=": "="}[e["op"]]
    return f"{signe} {_num(e['critere'], e['unite'])} {e['unite']}"


# ---------------------------------------------------------------- outils
def lister_exigences() -> str:
    """Liste les critères de la spécification SPEC-LFB-BAL-01 rév. C (exigences EX-01 à EX-05) :
    code, essai, paramètre, critère et unité. Utiliser ces codes dans verifier_valeur
    (par exemple EX-01-rebond, EX-02-pression, EX-04-rebond)."""
    ex = _exigences()
    lignes = ["Critères de SPEC-LFB-BAL-01 rév. C (Abibas Sport, fictif) :"]
    lignes += [f"{k} : {e['essai']}, {e['parametre']} · critère {_borne(e)}" for k, e in ex.items()]
    lignes.append("Rappel : l'outil compare une valeur à un critère ; la conformité est prononcée par l'ingénieure responsable.")
    _journal("lister_exigences", {}, f"{len(ex)} critères")
    return "\n".join(lignes)


def lire_resultats(sn: str) -> str:
    """Lit les résultats d'essai d'un spécimen dans la base du labo (lecture seule).

    sn : le numéro de série du spécimen, par exemple « L-0042 » ou « S/N L-0042 ».
    Répond une ligne par résultat : identifiant, exigence, paramètre, valeur, unité, remarque.
    Les valeurs sont rendues telles qu'enregistrées : « — » pour une donnée manquante,
    l'unité d'origine même si elle est fausse (°F). Ne compare rien : utiliser ensuite verifier_valeur.
    """
    cle = (sn or "").upper().replace("S/N", "").replace("S-N", "").strip()
    with _base() as cx:
        rangs = cx.execute("SELECT id, exigence, parametre, valeur, unite, sn, remarque FROM resultats "
                           "WHERE sn = ? ORDER BY rowid", (cle,)).fetchall()
        autres = [r[0] for r in cx.execute("SELECT DISTINCT sn FROM resultats ORDER BY sn")]
    if not rangs:
        sortie = f"Aucun résultat pour S/N {cle}. Spécimens présents : {', '.join('S/N ' + s for s in autres)}."
    else:
        lignes = [f"{len(rangs)} résultat(s) pour S/N {cle} (base du labo) :"]
        for i, ex, par, val, u, s, rem in rangs:
            lignes.append(f"{i} | {ex} | {par} | {_fmt(val)} | {u}" + (f" | {rem}" if rem else ""))
        if any(s != cle for s in autres):
            lignes.append("Note : d'autres spécimens ont des résultats (" + ", ".join(
                f"S/N {s}" for s in autres if s != cle) + ") : vérifier s'il y a une déviation.")
        sortie = "\n".join(lignes)
    _journal("lire_resultats", {"sn": sn}, f"{len(rangs)} ligne(s)")
    return sortie


def verifier_valeur(exigence: str, valeur_mesuree: float, unite: str) -> str:
    """Compare une valeur mesurée à un critère de SPEC-LFB-BAL-01 rév. C.

    exigence : un code comme EX-01-rebond, EX-02-tirs, EX-02-pression, EX-04-rebond (voir lister_exigences) ;
    EX-01 à EX-05 seuls désignent le critère principal (rebond, pression, prise d'eau, rebond à froid, perte de masse).
    valeur_mesuree : la valeur relevée (nombre ; 0,61 bar = 0.61).
    unite : l'unité de la valeur (cm, m, g, bar, %, km/h, tirs, positions, min, h, °C, cycles).
    Répond « dans le critère » ou « HORS CRITÈRE », avec l'écart au critère.
    Une valeur en °F est refusée : aucun verdict. Ne prononce jamais la conformité.
    """
    args = {"exigence": exigence, "valeur_mesuree": valeur_mesuree, "unite": unite}
    brut = (exigence or "").strip()
    code = ALIAS.get(brut, brut)
    ex = _exigences()
    e = ex.get(code)
    if e is None:
        _journal("verifier_valeur", args, "exigence inconnue")
        return f"Exigence inconnue : {exigence}. Codes disponibles : {', '.join(ex)}"
    try:
        txt = str(valeur_mesuree).strip().replace(",", ".").replace("−", "-")
        v = float(txt)
        if v.is_integer() and "." not in txt:
            v = int(v)
    except ValueError:
        _journal("verifier_valeur", args, "valeur illisible")
        return f"Valeur illisible : {valeur_mesuree}. Donner un nombre ; aucun verdict."
    u = _unite(unite)
    if u == "°F":
        celsius = (v - 32) * 5 / 9
        _journal("verifier_valeur", args, "unité refusée (°F)")
        return (f"UNITÉ REFUSÉE : {_fmt(v)} °F reçu pour {code}. Le glossaire Abibas impose °C. "
                f"Pour information : {_fmt(v)} °F = {_fmt(celsius)} °C. Aucun verdict : signaler l'unité du "
                "tableau à l'ingénieure et la faire corriger, sans conversion silencieuse dans le rapport.")
    if u != e["unite"]:
        _journal("verifier_valeur", args, "unité différente")
        return (f"Unité différente : {unite} reçu, {e['unite']} attendu pour {code}. "
                "Aucun verdict : vérifier la valeur ou signaler l'écart à l'ingénieure.")
    c, op = e["critere"], e["op"]
    ok = {">=": v >= c - 1e-9, "<=": v <= c + 1e-9, "=": abs(v - c) < 1e-9}[op]
    verdict = "dans le critère" if ok else "HORS CRITÈRE"
    ecart = ""
    if not ok:
        d = round(float(v) - float(c), 3)
        ecart = f" Écart : {'+' if d > 0 else ''}{_num(d, e['unite'])} {e['unite']} par rapport au critère."
    _journal("verifier_valeur", args, verdict)
    return (f"{code} ({e['essai']}, {e['parametre']}) : {_num(v, e['unite'])} {e['unite']} → {verdict} "
            f"[critère : {_borne(e)}].{ecart} Statut : à valider par l'ingénieure responsable.")


def chercher_nc(mot_cle: str) -> str:
    """Cherche dans le registre des non-conformités d’Abibas (base du labo, lecture seule).

    mot_cle : un mot ou une expression, sans tenir compte des majuscules ni des accents
    (exemples : « valve », « fuite », « froid », « couture », « LP-400 »).
    Répond les non-conformités trouvées (numéro, produit, essai, description, cause, action,
    statut, date de clôture), ou « aucune non-conformité trouvée ».
    Sert à répondre à « Avons-nous déjà eu ce problème ? Qu'avons-nous fait ? ».
    """
    cle = _sans_accent(mot_cle)
    with _base() as cx:
        cur = cx.execute("SELECT * FROM non_conformites ORDER BY id")
        noms = [c[0] for c in cur.description]
        trouvees = [dict(zip(noms, r)) for r in cur.fetchall()
                    if cle and cle in _sans_accent(" ".join(str(x) for x in r if x))]
    if not trouvees:
        sortie = f"Aucune non-conformité trouvée pour « {mot_cle} »."
    else:
        blocs = [f"{len(trouvees)} non-conformité(s) trouvée(s) pour « {mot_cle} » :"]
        blocs += [" · ".join(f"{k} : {v}" for k, v in l.items() if v) for l in trouvees]
        sortie = "\n".join(blocs)
    _journal("chercher_nc", {"mot_cle": mot_cle}, ", ".join(l["id"] for l in trouvees) or "aucune")
    return sortie


def calculer_devis(essais: list[str], nb_specimens: int, delai_jours_ouvrables: int) -> str:
    """Calcule un devis d'essais avec la grille tarifaire 2026 d’Abibas (CAD, avant taxes).

    essais : liste de noms parmi rebond, tirs, absorption, froid, usure.
    nb_specimens : nombre TOTAL de spécimens (1 = pas de spécimen supplémentaire).
    delai_jours_ouvrables : délai demandé par le client pour recevoir les résultats (3 semaines = 15).
    Règles : chaque spécimen supplémentaire = +35 % du prix de chaque essai ; un rapport et revue = 950 $ ;
    durée standard = somme des jours d'essais + 5 jours de rapport ; urgence = +20 % sur le total
    seulement si le délai demandé est inférieur à 10 jours ouvrables. Taxes en sus ; validité 30 jours.
    Répond les lignes détaillées et le total. Ne remplace pas la validation du chargé de projet.
    """
    args = {"essais": essais, "nb_specimens": nb_specimens, "delai_jours_ouvrables": delai_jours_ouvrables}
    with _base() as cx:
        tarifs = {r[0]: (float(r[1]), int(r[2])) for r in cx.execute("SELECT essai, prix, delai_jours FROM tarifs")}
    if isinstance(essais, str):
        essais = essais.replace(";", ",").split(",")
    cles = []
    for e in essais:
        k = ESSAIS.get(_sans_accent(e))
        if not k:
            _journal("calculer_devis", args, "essai inconnu")
            return f"Essai inconnu : {e}. Essais possibles : rebond, tirs, absorption, froid, usure."
        cles.append(k)
    lignes, sous_total, jours = [], 0.0, 0
    for k in cles:
        prix, j = tarifs[k]
        sous_total += prix
        jours += j
        lignes.append(f"- {k} : {_dollars(prix)} ({j} jour{'s' if j > 1 else ''} ouvrable{'s' if j > 1 else ''})")
    supp = max(int(nb_specimens) - 1, 0)
    m_supp = sous_total * 0.35 * supp
    rapport, j_rapport = tarifs["rapport"]
    total = sous_total + m_supp + rapport
    duree = jours + j_rapport
    urgence = int(delai_jours_ouvrables) < 10
    maj = total * 0.20 if urgence else 0.0
    lignes += [
        f"Sous-total essais : {_dollars(sous_total)}",
        f"Spécimens supplémentaires : {supp} × 35 % × {_dollars(sous_total)} = {_dollars(m_supp)}",
        f"Rapport et revue : {_dollars(rapport)}",
        f"Majoration d'urgence : {_dollars(maj) + ' (+20 %)' if urgence else 'non applicable'}",
        f"TOTAL : {_dollars(total + maj)} avant taxes (taxes en sus, validité 30 jours)",
        f"Durée standard : {jours} j d'essais + {j_rapport} j de rapport = {duree} jours ouvrables ; "
        f"délai demandé : {delai_jours_ouvrables} jours ouvrables.",
        ("Urgence : délai demandé inférieur à 10 jours ouvrables, +20 % appliqués." if urgence else
         "Pas d'urgence : le délai demandé n'est pas inférieur à 10 jours ouvrables."),
    ]
    if duree > int(delai_jours_ouvrables):
        lignes.append("ATTENTION : la durée standard dépasse le délai demandé ; à discuter avec le chargé de projet.")
    lignes.append("À valider par le chargé de projet (Karim Haddad) avant tout envoi.")
    _journal("calculer_devis", args, f"total {_dollars(total + maj)} avant taxes")
    return "Devis selon la grille tarifaire 2026 :\n" + "\n".join(lignes)


# ---------------------------------------------------------------- essai et lancement
def _test():
    try:  # Windows : affichage UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(lire_resultats("L-0042"), "\n")
    for c in [("EX-01-rebond", 132, "cm"), ("EX-01-hauteur", 1.8, "m"), ("EX-02-tirs", 750, "tirs"),
              ("EX-02-pression", 0.74, "bar"), ("EX-02-pression", 0.61, "bar"), ("EX-03-prise-eau", 6, "%"),
              ("EX-04-palier", -4, "°F"), ("EX-04-rebond", 116, "cm"), ("EX-05-cycles", 450, "cycles")]:
        print(f"verifier_valeur{c} -> {verifier_valeur(*c)}")
    print(f"\nchercher_nc('valve') ->\n{chercher_nc('valve')}")
    print(f"\ncalculer_devis(['rebond', 'absorption', 'froid'], 2, 15) ->\n"
          f"{calculer_devis(['rebond', 'absorption', 'froid'], 2, 15)}")


def _serveur():
    try:  # SDK MCP 2.x
        from mcp.server.mcpserver import MCPServer as Serveur
    except ImportError:
        try:  # SDK MCP 1.x
            from mcp.server.fastmcp import FastMCP as Serveur
        except ImportError:
            print("ERREUR : SDK MCP absent. Installez-le : pip install mcp "
                  "(ou lancez --test pour essayer les fonctions sans le SDK).", file=sys.stderr)
            sys.exit(3)
    serveur = Serveur("verifier-valeur")
    for outil in (lister_exigences, lire_resultats, verifier_valeur, chercher_nc, calculer_devis):
        serveur.tool()(outil)
    return serveur


if __name__ == "__main__":
    if "--test" in sys.argv:
        _test()
    else:
        _serveur().run()
