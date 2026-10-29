#!/usr/bin/env python3
"""Calcule un devis d'essais à partir de base-abibas/5-prix/Grille tarifaire 2026.xlsx.

Le calcul est fait par ce script, jamais de tête. Même entrée, même total.

Usage :
    python3 outils/calcul_devis.py --essais rebond,absorption,froid --specimens 2 --delai-souhaite 15
Options :
    --essais          codes ou noms : rebond, tirs, absorption, froid, usure (séparés par des virgules)
    --specimens       nombre total de spécimens (défaut 1) ; chaque spécimen en plus = +35 % du prix de chaque essai
    --rapports        nombre de rapports (défaut 1)
    --delai-souhaite  délai demandé par le client, en jours ouvrables (3 semaines = 15)
Règles (grille 2026) : urgence = +20 % sur le total si les résultats sont demandés en moins de
10 jours ouvrables ; prix en CAD avant taxes ; taxes en sus ; validité 30 jours.
"""
import argparse
import os
import sys
for _flux in (sys.stdout, sys.stderr):  # Windows : affichage UTF-8 (−, ≥, Ω)
    try:
        _flux.reconfigure(encoding="utf-8")
    except Exception:
        pass
import unicodedata

try:
    import openpyxl
except ImportError:
    print("ERREUR : installez la dépendance : pip install openpyxl")
    sys.exit(3)

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRILLE = os.path.join(RACINE, "base-abibas", "5-prix", "Grille tarifaire 2026.xlsx")
TAUX_SPECIMEN = 0.35
TAUX_URGENCE = 0.20
SEUIL_URGENCE = 10  # jours ouvrables
SYNONYMES = {"rebond": "REBOND", "tirs": "TIRS", "tirs repetes": "TIRS", "tir": "TIRS",
             "absorption": "EAU", "absorption d'eau": "EAU", "absorption d’eau": "EAU", "eau": "EAU",
             "froid": "FROID", "usure": "USURE", "abrasion": "USURE"}


def sans_accent(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower().strip()


def lire_grille():
    ws = openpyxl.load_workbook(GRILLE, data_only=True).active
    grille, entete = {}, None
    for r in ws.iter_rows(values_only=True):
        if r and r[0] == "Code":
            entete = True
            continue
        if entete and r and r[0] and r[2] is not None:
            grille[r[0]] = {"essai": r[1], "prix": float(r[2]), "delai": int(r[3])}
    return grille


def dollars(x):
    return f"{x:,.0f}".replace(",", " ") + " $"


def main():
    ap = argparse.ArgumentParser(description="Devis d'essais Abibas (grille 2026)")
    ap.add_argument("--essais", required=True)
    ap.add_argument("--specimens", type=int, default=1)
    ap.add_argument("--rapports", type=int, default=1)
    ap.add_argument("--delai-souhaite", type=int, default=None)
    a = ap.parse_args()

    grille = lire_grille()
    codes = []
    for e in a.essais.split(","):
        k = SYNONYMES.get(sans_accent(e), e.strip().upper())
        if k not in grille or k == "RAPPORT":
            print(f"ERREUR : essai inconnu dans la grille : {e}")
            sys.exit(2)
        codes.append(k)

    print("Devis calculé par outils/calcul_devis.py · Grille tarifaire 2026 (CAD, avant taxes)\n")
    sous_total = 0.0
    for k in codes:
        g = grille[k]
        sous_total += g["prix"]
        print(f"  {g['essai']:<32} {dollars(g['prix']):>10}   ({g['delai']} jour{'s' if g['delai'] > 1 else ''} ouvrable{'s' if g['delai'] > 1 else ''})")
    print(f"  {'Sous-total essais':<32} {dollars(sous_total):>10}")

    supp = max(a.specimens - 1, 0)
    montant_supp = sous_total * TAUX_SPECIMEN * supp
    print(f"  {'Spécimens supplémentaires':<32} {dollars(montant_supp):>10}   "
          f"({supp} × 35 % × {dollars(sous_total)})")

    rapport = grille["RAPPORT"]["prix"] * a.rapports
    print(f"  {'Rapport et revue':<32} {dollars(rapport):>10}   ({a.rapports} rapport(s))")

    total = sous_total + montant_supp + rapport
    j_essais = sum(grille[k]["delai"] for k in codes)
    j_rapport = grille["RAPPORT"]["delai"]
    delai = j_essais + j_rapport
    urgence = a.delai_souhaite is not None and a.delai_souhaite < SEUIL_URGENCE
    maj = total * TAUX_URGENCE if urgence else 0.0
    print(f"  {'Majoration d’urgence':<32} {dollars(maj) if urgence else 'non applicable':>10}")
    print(f"  {'TOTAL AVANT TAXES':<32} {dollars(total + maj):>10}   (taxes en sus, validité 30 jours)\n")

    print(f"Délai standard : {j_essais} jours d’essais + {j_rapport} jours de rapport = {delai} jours ouvrables.")
    if a.delai_souhaite is not None:
        print(f"Délai souhaité par le client : {a.delai_souhaite} jours ouvrables.")
        if urgence:
            print(f"Urgence : résultats demandés en moins de {SEUIL_URGENCE} jours ouvrables → +20 % sur le total.")
        else:
            print(f"Pas d’urgence : le délai demandé n’est pas inférieur à {SEUIL_URGENCE} jours ouvrables.")
        if delai > a.delai_souhaite:
            print("ATTENTION : le délai standard dépasse le délai souhaité. À discuter avec le chargé de projet.")
        else:
            print("Le délai standard tient dans le délai souhaité.")
    print("\nÀ valider par le chargé de projet (Karim Haddad) avant tout envoi.")


if __name__ == "__main__":
    main()
