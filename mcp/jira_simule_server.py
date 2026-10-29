#!/usr/bin/env python3
"""
Serveur MCP « jira-simule » : un Jira de démonstration pour le projet qualité QUAL d’Abibas.
Démo formation IA, vendredi 2 (D10). Tout est fictif.

Trois outils :
- chercher_tickets(texte) : cherche les tickets semblables (lecture) ;
- lister_tickets() : liste tous les tickets (lecture) ;
- creer_ticket(champs) : crée un ticket « Réclamation client », toujours dans le projet QUAL,
  toujours au statut « À trier », avec l'étiquette « cree-par-IA ».

Les tickets sont rangés dans donnees/jira-simule.json (remise à zéro : python3 outils/reinitialiser_jira.py).
Chaque appel ajoute une ligne à donnees/journal-mcp.log.

Lancement : python3 mcp/jira_simule_server.py   (Claude le lance tout seul via .mcp.json)
Essai sans Claude : python3 mcp/jira_simule_server.py --test
Dépendance : pip install mcp. Sans le SDK, les fonctions restent importables et testables.
"""
import datetime
import json
import os
import re
import sys
import unicodedata

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAGASIN = os.path.join(RACINE, "donnees", "jira-simule.json")
JOURNAL = os.path.join(RACINE, "donnees", "journal-mcp.log")

PROJET = "QUAL"
STATUT_CREATION = "À trier"
ETIQUETTE_IA = "cree-par-IA"
RESUME_MAX = 80

# Les deux tickets existants (état initial du Jira simulé).
TICKETS_INITIAUX = [
    {
        "cle": "QUAL-41", "projet": "QUAL", "type": "Réclamation client",
        "resume": "Belmont · ballon 77 · logo effacé après 3 matchs",
        "client": "Ligue de foot de Belmont, saison 2027", "produit": "Ballon d’entraînement LP-300",
        "sn": "S/N K-1207", "symptome": "Logo de la ligue effacé après 3 matchs ; le ballon garde sa pression.",
        "date_incident": "2026-08-12", "nb_unites": 1, "unites": "ballon 77",
        "gravite": "Mineure (confirmée)", "exigence": "Aucune exigence de SPEC-LFB-BAL-01",
        "cas_semblables": "Aucun", "pieces_jointes": "photo-logo.jpg",
        "statut": "Clôturé", "etiquettes": [], "demandeur": "Isabelle Roy",
        "resolution": "Nouvelle encre d’impression du logo.", "cree_le": "2026-08-13T09:20:00",
    },
    {
        "cle": "QUAL-42", "projet": "QUAL", "type": "Réclamation client",
        "resume": "Belmont · ballon 15 · couture qui prend l’eau après lavage",
        "client": "Ligue de foot de Belmont, saison 2027", "produit": "Ballon LP-400",
        "sn": "S/N K-0388", "symptome": "Le ballon est lourd et mou après un lavage au jet ; l’eau entre par une couture près de la valve.",
        "date_incident": "2026-06-03", "nb_unites": 1, "unites": "ballon 15",
        "gravite": "Majeure (confirmée)", "exigence": "EX-03 (absorption d’eau)",
        "cas_semblables": "NC-2025-021 (prise d’eau à une couture, LP-400)", "pieces_jointes": "photo-couture.jpg",
        "statut": "Clôturé", "etiquettes": [], "demandeur": "Isabelle Roy",
        "resolution": "Remplacement par un ballon thermocollé (action de NC-2025-021).", "cree_le": "2026-06-04T14:05:00",
    },
]

# Champs obligatoires du modèle de ticket qualité (clé interne → libellé du modèle).
OBLIGATOIRES = {
    "projet": "Projet", "type": "Type", "resume": "Résumé", "client": "Client", "produit": "Produit",
    "sn": "S/N", "symptome": "Symptôme", "date_incident": "Date de l'incident",
    "nb_unites": "Nombre d'unités touchées", "gravite": "Gravité proposée",
    "exigence": "Exigence possiblement touchée", "cas_semblables": "Cas semblables",
    "pieces_jointes": "Pièces jointes", "statut": "Statut", "etiquettes": "Étiquette", "demandeur": "Demandeur",
}
SYNONYMES = {
    "resume": "resume", "summary": "resume", "titre": "resume", "symptome": "symptome",
    "date_de_l_incident": "date_incident", "date": "date_incident", "date_incident": "date_incident",
    "nombre_d_unites_touchees": "nb_unites", "nombre_unites": "nb_unites", "unites_touchees": "nb_unites",
    "nb_unites": "nb_unites", "gravite_proposee": "gravite", "gravite": "gravite",
    "exigence_possiblement_touchee": "exigence", "exigence": "exigence",
    "cas_semblables": "cas_semblables", "pieces_jointes": "pieces_jointes", "piece_jointe": "pieces_jointes",
    "etiquette": "etiquettes", "etiquettes": "etiquettes", "labels": "etiquettes",
    "s_n": "sn", "sn": "sn", "numero_de_serie": "sn", "type_de_ticket": "type",
}
MOTS_VIDES = {"les", "des", "une", "est", "pas", "plus", "pour", "dans", "avec", "sur", "par", "qui",
              "que", "aux", "apres", "depuis", "son", "ses", "the", "and"}


def _sans_accent(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "")) if unicodedata.category(c) != "Mn").lower()


def _cle_champ(k):
    k = re.sub(r"[^a-z0-9]+", "_", _sans_accent(k)).strip("_")
    return SYNONYMES.get(k, k)


def _journal(outil, arguments, resultat):
    try:
        court = " ".join(str(resultat).split())[:140]
        with open(JOURNAL, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} | jira-simule | {outil} | "
                    f"{json.dumps(arguments, ensure_ascii=False)} | {court}\n")
    except Exception:
        pass


def reinitialiser():
    """Remet le Jira simulé dans son état initial (QUAL-41 et QUAL-42)."""
    os.makedirs(os.path.dirname(MAGASIN), exist_ok=True)
    with open(MAGASIN, "w", encoding="utf-8") as f:
        json.dump({"projet": PROJET, "tickets": TICKETS_INITIAUX}, f, ensure_ascii=False, indent=2)


def _charger():
    if not os.path.exists(MAGASIN):
        reinitialiser()
    with open(MAGASIN, encoding="utf-8") as f:
        return json.load(f)


def _resume_ticket(t):
    return (f"{t['cle']} · {t['statut']} · {t['resume']} · {t.get('sn', '')} · gravité : {t.get('gravite', '')}"
            f" · cas semblables : {t.get('cas_semblables', '')}"
            + (f" · résolution : {t['resolution']}" if t.get("resolution") else ""))


def chercher_tickets(texte: str) -> str:
    """Cherche dans le Jira qualité (projet QUAL) les tickets semblables à un texte (lecture seule).

    texte : quelques mots-clés du problème, par exemple « dégonflé », « couture ouverte »,
    « eau », « logo effacé ». La recherche ignore les majuscules et les accents ; elle classe les tickets
    par nombre de mots trouvés. Répond les tickets trouvés (clé, statut, résumé, S/N, gravité,
    cas semblables, résolution), ou « aucun ticket semblable ».
    """
    mots = [m for m in re.findall(r"[a-z0-9-]{3,}", _sans_accent(texte)) if m not in MOTS_VIDES]
    scores = []
    for t in _charger()["tickets"]:
        corps = _sans_accent(" ".join(str(v) for v in t.values()))
        n = sum(1 for m in mots if m in corps)
        if n:
            scores.append((n, t))
    scores.sort(key=lambda x: -x[0])
    if not scores:
        sortie = f"Aucun ticket semblable pour « {texte} »."
    else:
        sortie = f"{len(scores)} ticket(s) trouvé(s) pour « {texte} » (du plus proche au moins proche) :\n" + \
                 "\n".join(f"- ({n} mot(s)) " + _resume_ticket(t) for n, t in scores)
    _journal("chercher_tickets", {"texte": texte}, ", ".join(t["cle"] for _, t in scores) or "aucun")
    return sortie


def lister_tickets() -> str:
    """Liste tous les tickets du Jira qualité simulé (projet QUAL), du plus ancien au plus récent (lecture seule)."""
    tickets = _charger()["tickets"]
    _journal("lister_tickets", {}, f"{len(tickets)} ticket(s)")
    return f"{len(tickets)} ticket(s) dans QUAL :\n" + "\n".join("- " + _resume_ticket(t) for t in tickets)


def creer_ticket(champs: dict) -> str:
    """Crée un ticket « Réclamation client » dans le Jira qualité, au format du Modèle de ticket qualité.

    champs : un objet avec les 16 champs obligatoires du modèle :
      projet (toujours « QUAL »), type (« Réclamation client »), resume (80 caractères au maximum),
      client, produit, sn (ex. « S/N L-0311 »), symptome, date_incident, nb_unites (nombre),
      gravite (« Critique », « Majeure » ou « Mineure », toujours suivie de « à confirmer »),
      exigence (ex. « EX-03 (absorption d’eau) »), cas_semblables (tickets QUAL et NC), pieces_jointes,
      statut (toujours « À trier »), etiquettes (contient « cree-par-IA »), demandeur.
    Règles imposées par le serveur : projet QUAL seulement ; statut « À trier » seulement ;
    gravité « à confirmer » ; résumé ≤ 80 caractères ; l'étiquette « cree-par-IA » est ajoutée si elle manque.
    Ne pas créer de ticket pour ce qui n'est pas une réclamation (facture, question, offre).
    Répond la clé du ticket créé (ex. QUAL-43), ou la liste des champs à corriger.
    """
    if isinstance(champs, str):
        try:
            champs = json.loads(champs)
        except ValueError:
            return "REFUSÉ : champs illisibles (donner un objet JSON)."
    t = {_cle_champ(k): v for k, v in (champs or {}).items()}
    t.setdefault("statut", STATUT_CREATION)
    et = t.get("etiquettes") or []
    et = [e.strip() for e in (et.split(",") if isinstance(et, str) else et) if str(e).strip()]
    if ETIQUETTE_IA not in et:
        et.append(ETIQUETTE_IA)
    t["etiquettes"] = et

    erreurs = []
    if str(t.get("projet", "")).strip().upper() != PROJET:
        erreurs.append(f"projet « {t.get('projet', '')} » refusé : seul le projet {PROJET} est permis")
    if str(t.get("statut", "")).strip() != STATUT_CREATION:
        erreurs.append(f"statut « {t.get('statut')} » refusé : un ticket créé par l'IA est toujours « {STATUT_CREATION} »")
    manquants = [lib for k, lib in OBLIGATOIRES.items() if t.get(k) in (None, "", [])]
    if manquants:
        erreurs.append("champs obligatoires manquants : " + ", ".join(manquants))
    if len(str(t.get("resume", ""))) > RESUME_MAX:
        erreurs.append(f"résumé trop long : {len(str(t['resume']))} caractères (80 au maximum)")
    if t.get("gravite") and "a confirmer" not in _sans_accent(t["gravite"]):
        erreurs.append("gravité refusée : elle est proposée, jamais décidée (ajouter « à confirmer »)")
    if erreurs:
        _journal("creer_ticket", {k: t.get(k) for k in ("projet", "statut", "resume")}, "REFUSÉ : " + " ; ".join(erreurs))
        return "REFUSÉ, aucun ticket créé :\n- " + "\n- ".join(erreurs)

    data = _charger()
    numeros = [int(x["cle"].split("-")[1]) for x in data["tickets"]]
    t["cle"] = f"{PROJET}-{max(numeros, default=0) + 1}"
    t["projet"] = PROJET
    t["cree_le"] = datetime.datetime.now().isoformat(timespec="seconds")
    data["tickets"].append(t)
    with open(MAGASIN, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    _journal("creer_ticket", {"resume": t.get("resume")}, f"créé {t['cle']}")
    return (f"Ticket créé : {t['cle']} · statut « {STATUT_CREATION} » · étiquette {ETIQUETTE_IA}. "
            "Un humain le trie et confirme la gravité. Aucune réponse n'a été envoyée au client.")


def _test():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(lister_tickets(), "\n")
    print(chercher_tickets("ballon dégonflé après la pluie, couture ouverte, eau"), "\n")
    print(creer_ticket({"projet": "QUAL", "statut": "En cours", "resume": "essai"}))


def _serveur():
    try:  # SDK MCP 2.x
        from mcp.server.mcpserver import MCPServer as Serveur
    except ImportError:
        try:  # SDK MCP 1.x
            from mcp.server.fastmcp import FastMCP as Serveur
        except ImportError:
            print("ERREUR : SDK MCP absent. Installez-le : pip install mcp.", file=sys.stderr)
            sys.exit(3)
    serveur = Serveur("jira-simule")
    for outil in (chercher_tickets, lister_tickets, creer_ticket):
        serveur.tool()(outil)
    return serveur


if __name__ == "__main__":
    if "--test" in sys.argv:
        _test()
    else:
        _serveur().run()
