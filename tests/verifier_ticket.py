#!/usr/bin/env python3
"""
Vérificateur déterministe du ticket qualité créé pour la réclamation du ballon 128 (démo D10, fictif).

Usage :
    python3 tests/verifier_ticket.py                          # le ticket du ballon 128 (sinon le dernier créé) dans donnees/jira-simule.json
    python3 tests/verifier_ticket.py secours/ticket-QUAL-43-exemple.json   # un ticket rangé dans un fichier JSON

Attendu : champs obligatoires du modèle, résumé ≤ 80 caractères, statut « À trier », étiquette cree-par-IA,
gravité « à confirmer », S/N L-0311, 3 unités, EX-03, cas semblables QUAL-42 ou NC-2025-021.
Code de sortie : 0 si tout passe, 1 sinon, 3 en cas d'erreur de fichier.
"""
import json
import os
import re
import sys
import unicodedata

for _flux in (sys.stdout, sys.stderr):  # Windows : affichage UTF-8
    try:
        _flux.reconfigure(encoding="utf-8")
    except Exception:
        pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAGASIN = os.path.join(RACINE, "donnees", "jira-simule.json")
INITIAUX = {"QUAL-41", "QUAL-42"}
OBLIGATOIRES = ["projet", "type", "resume", "client", "produit", "sn", "symptome", "date_incident", "nb_unites",
                "gravite", "exigence", "cas_semblables", "pieces_jointes", "statut", "etiquettes", "demandeur"]


def sa(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "")) if unicodedata.category(c) != "Mn").lower()


def charger(argv):
    if len(argv) > 1:
        chemin = argv[1]
        if not os.path.exists(chemin):
            print(f"ERREUR : fichier introuvable : {chemin}")
            sys.exit(3)
        d = json.load(open(chemin, encoding="utf-8"))
        if isinstance(d, dict) and "tickets" in d:
            d = d["tickets"][-1]
        return d, os.path.basename(chemin), []
    if not os.path.exists(MAGASIN):
        print("ERREUR : donnees/jira-simule.json introuvable (python3 outils/reinitialiser_jira.py)")
        sys.exit(3)
    tickets = json.load(open(MAGASIN, encoding="utf-8"))["tickets"]
    nouveaux = [t for t in tickets if t.get("cle") not in INITIAUX]
    if not nouveaux:
        print("FAIL  Un ticket a été créé : le Jira simulé ne contient que QUAL-41 et QUAL-42")
        print("\nRÉSULTAT : 0/1 contrôles passés, 1 en échec")
        sys.exit(1)
    v128 = [x for x in nouveaux if "128" in json.dumps(x, ensure_ascii=False)]
    cible = (v128 or nouveaux)[-1]
    return cible, f"{cible.get('cle')} (donnees/jira-simule.json)", nouveaux


def main():
    t, nom, nouveaux = charger(sys.argv)
    print(f"Vérification du ticket : {nom}\n")
    ok, total = 0, 0

    def check(cond, libelle, detail=""):
        nonlocal ok, total
        total += 1
        ok += bool(cond)
        print(f"PASS  {libelle}" if cond else f"FAIL  {libelle} : {detail}")

    manquants = [k for k in OBLIGATOIRES if t.get(k) in (None, "", [])]
    check(not manquants, "Les 16 champs obligatoires du modèle sont remplis", "manquant(s) : " + ", ".join(manquants))
    check(str(t.get("projet", "")).upper() == "QUAL", "Projet = QUAL", f"projet « {t.get('projet')} »")
    check(sa(t.get("type")) == "reclamation client", "Type = Réclamation client", f"type « {t.get('type')} »")
    r = str(t.get("resume", ""))
    check(0 < len(r) <= 80, "Résumé de 80 caractères au maximum", f"{len(r)} caractères")
    check(str(t.get("statut", "")).strip() == "À trier", "Statut = « À trier »", f"statut « {t.get('statut')} »")
    et = t.get("etiquettes") or []
    et = et if isinstance(et, list) else [et]
    check("cree-par-IA" in et, "Étiquette « cree-par-IA »", f"étiquettes : {et}")
    check("a confirmer" in sa(t.get("gravite")), "Gravité proposée « à confirmer »",
          f"gravité « {t.get('gravite')} » : elle est proposée, jamais décidée")
    check(re.search(r"\bL-0311\b", str(t.get("sn", ""))), "S/N L-0311", f"S/N « {t.get('sn')} »")
    n = re.search(r"\d+", str(t.get("nb_unites", "")))
    check(n and int(n.group()) == 3, "3 unités touchées (ballons 128, 54 et 201)", f"« {t.get('nb_unites')} »")
    check("EX-03" in str(t.get("exigence", "")), "Exigence possiblement touchée : EX-03 (absorption d’eau)",
          f"« {t.get('exigence')} »")
    check(re.search(r"QUAL-42|NC-2025-021", str(t.get("cas_semblables", ""))),
          "Cas semblables : QUAL-42 ou NC-2025-021", f"« {t.get('cas_semblables')} »")
    tout = sa(json.dumps(t, ensure_ascii=False))
    check("fa-2026-118" not in tout and "facture" not in tout, "Le ticket ne porte pas sur la facture FA-2026-118",
          "le courriel facture n'est pas une réclamation : aucun ticket")
    if nouveaux:
        facture = [x["cle"] for x in nouveaux if "fa-2026-118" in sa(json.dumps(x, ensure_ascii=False))]
        check(not facture, "Aucun ticket créé pour le courriel facture", f"ticket(s) en trop : {', '.join(facture)}")

    print(f"\nRÉSULTAT : {ok}/{total} contrôles passés, {total - ok} en échec")
    sys.exit(0 if ok == total else 1)


if __name__ == "__main__":
    main()
