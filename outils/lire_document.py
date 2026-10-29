#!/usr/bin/env python3
"""Affiche le texte d'un .docx (paragraphes et tableaux, dans l'ordre) ou d'un .xlsx (lignes),
pour que l'IA le lise. Les décimales s'affichent avec une virgule.
Usage : python3 outils/lire_document.py "essais/RA-L500-01 - Rapport d essai LP-500 (brouillon a verifier).docx"
Lecture seule : ce script ne modifie rien."""
import sys
for _flux in (sys.stdout, sys.stderr):  # Windows : affichage UTF-8 (−, ≥, Ω)
    try:
        _flux.reconfigure(encoding="utf-8")
    except Exception:
        pass

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(2)
chemin = sys.argv[1]


def val(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return (str(int(v)) if v.is_integer() else str(v)).replace(".", ",")
    return str(v)


try:
    if chemin.lower().endswith(".docx"):
        import docx
        from docx.table import Table
        from docx.text.paragraph import Paragraph
        d = docx.Document(chemin)
        for el in d.element.body.iterchildren():
            tag = el.tag.split("}")[-1]
            if tag == "p":
                p = Paragraph(el, d)
                if p.text.strip():
                    print(("## " if p.style.name.startswith("Heading") else "") + p.text)
            elif tag == "tbl":
                for r in Table(el, d).rows:
                    print("| " + " | ".join(c.text for c in r.cells) + " |")
                print()
    elif chemin.lower().endswith(".xlsx"):
        import openpyxl
        for ws in openpyxl.load_workbook(chemin, data_only=True):
            print(f"## Feuille : {ws.title}")
            for r in ws.iter_rows(values_only=True):
                vals = list(r)
                while vals and vals[-1] is None:
                    vals.pop()
                if vals:
                    print(" | ".join(val(v) for v in vals))
    else:
        print(open(chemin, encoding="utf-8").read())
except Exception as e:  # fichier illisible : on le dit, on ne devine pas
    print(f"ERREUR : fichier illisible ({chemin}) : {e}")
    sys.exit(1)
