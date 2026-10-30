#!/usr/bin/env python3
"""
Vérificateur déterministe d'une leçon apprise tirée d'une non-conformité (skill lecon-apprise, fictif).

Usage :
    python3 .claude/skills/lecon-apprise/scripts/verifier_lecon.py travail/lecon-NC-2025-021.md

Compare la ligne proposée à la NC du registre des non-conformités et au registre des leçons apprises.
Code de sortie : 0 si tout passe, 1 sinon, 3 en cas d'erreur de fichier.
"""
import os
import re
import sys
import unicodedata

for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8")
    except Exception:
        pass

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
REGISTRE_NC = os.path.join(RACINE, "connaissances", "2-savoir", "Registre des non-conformites.md")
REGISTRE_LA = os.path.join(RACINE, "connaissances", "2-savoir", "Lecons apprises.md")


def sa(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "")) if unicodedata.category(c) != "Mn").lower()


def lignes_tableau(texte):
    """Les lignes de données des tableaux Markdown, en listes de cellules."""
    out = []
    for l in texte.splitlines():
        l = l.strip()
        if l.startswith("|") and not re.match(r"^\|[\s|:-]+\|$", l):
            out.append([c.strip() for c in l.strip("|").split("|")])
    return out


def nombres(s):
    """Les nombres d'un texte, normalisés (espace des milliers retirée)."""
    return {re.sub(r"[\s  ]", "", n) for n in re.findall(r"\d+(?:[\s  ]\d{3})*(?:,\d+)?", s)}


def lire(chemin):
    if not os.path.exists(chemin):
        print(f"ERREUR : fichier introuvable : {chemin}")
        sys.exit(3)
    return open(chemin, encoding="utf-8").read()


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(3)
    fiche = lire(sys.argv[1])
    nc_txt, la_txt = lire(REGISTRE_NC), lire(REGISTRE_LA)
    print(f"Vérification de la leçon : {sys.argv[1]}\n")
    ok, total = 0, 0

    def check(cond, libelle, detail=""):
        nonlocal ok, total
        total += 1
        ok += bool(cond)
        print(f"PASS  {libelle}" if cond else f"FAIL  {libelle} : {detail}")

    lignes = [l for l in lignes_tableau(fiche) if sa(l[0]) != "n°" and len(l) >= 2]
    check(len(lignes) == 1, "Une seule ligne de leçon", f"{len(lignes)} ligne(s) trouvée(s)")
    if not lignes:
        print(f"\nRÉSULTAT : {ok}/{total} contrôles passés, {total - ok} en échec")
        sys.exit(1)
    ligne = lignes[0]
    check(len(ligne) == 5 and all(ligne), "Cinq colonnes remplies (N°, date, leçon, origine, ce que l’on fait)",
          f"{len(ligne)} colonne(s), vide(s) : {[i + 1 for i, c in enumerate(ligne) if not c]}")
    ligne += [""] * (5 - len(ligne))
    num, date, lecon, origine, action = ligne[:5]

    ids = re.findall(r"NC-\d{4}-\d{3}", origine)
    check(ids, "L’origine cite une NC (NC-AAAA-NNN)", f"origine « {origine} »")
    nc_id = ids[0] if ids else ""
    nc = next((l for l in lignes_tableau(nc_txt) if l and l[0] == nc_id), None)
    check(nc, f"{nc_id or 'La NC'} existe dans le registre des non-conformités", "introuvable")
    if nc:
        statut, cloture = nc[7] if len(nc) > 7 else "", nc[8] if len(nc) > 8 else ""
        check(sa(statut).startswith("cloture"), f"{nc_id} est clôturée", f"statut « {statut} »")
        m = re.search(r"(\d{1,2})\s+(\S+)\s+(\d{4})", cloture)
        attendu = f"{m.group(2)} {m.group(3)}" if m else ""
        check(attendu and sa(date) == sa(attendu), "Date = mois et année de clôture de la NC",
              f"« {date} » écrit, « {attendu or cloture} » attendu")
        source = " ".join(nc) + " " + nc_id
        permis = nombres(source) | {"1", "2", "3", "4", "5"}  # petites quantités de langue courante
        en_trop = sorted(nombres(" ".join([lecon, origine, action])) - permis - nombres(nc_id))
        check(not en_trop, "Aucun nombre absent de la NC (rien d’inventé ni de converti)", ", ".join(en_trop))
    deja = [l[0] for l in lignes_tableau(la_txt) if nc_id and len(l) > 3 and nc_id in l[3]]
    check(not deja, f"Aucune leçon ne cite déjà {nc_id or 'la NC'}", f"déjà tirée : {', '.join(deja)}")
    check(re.fullmatch(r"LA-\d{2,}|\[À COMPLÉTER\]", num), "N° de la forme LA-xx ou [À COMPLÉTER]", f"« {num} »")
    check(re.search(r"Brouillon rédigé avec l.aide de l.IA, à vérifier", fiche),
          "Mention « Brouillon rédigé avec l’aide de l’IA, à vérifier »", "absente")
    interdits = re.findall(r"\b(conformes?|qualifiee?s?)\b", sa(" ".join(ligne)))  # sa() retire les accents
    check(not interdits, "La conformité n’est pas prononcée (mots réservés à Julie Tremblay)", ", ".join(interdits))
    check(not re.search(r"\d\.\d", " ".join(ligne)), "Virgule décimale", "un point décimal est écrit")

    print(f"\nRÉSULTAT : {ok}/{total} contrôles passés, {total - ok} en échec")
    sys.exit(0 if ok == total else 1)


if __name__ == "__main__":
    main()
