#!/usr/bin/env python3
"""Crée la base de données du labo : donnees/abibas-labo.db (SQLite).

Mêmes données que les fichiers Excel de base-abibas/ et essais/ (tout est fictif).
Tables :
    exigences(id, essai, parametre, operateur, valeur_critere, unite, revision)
    resultats(id, exigence, parametre, valeur, unite, sn, remarque)
    non_conformites(id, produit, essai, description, cause, action, statut, date_cloture)
    tarifs(essai, prix, delai_jours)

Usage : python3 outils/creer_base.py      (recrée la base à neuf)
Dépendance : aucune (sqlite3 est fourni avec Python).
"""
import os
import sqlite3
import sys

for _flux in (sys.stdout, sys.stderr):  # Windows : affichage UTF-8
    try:
        _flux.reconfigure(encoding="utf-8")
    except Exception:
        pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RACINE, "donnees", "abibas-labo.db")
M = "−"  # signe moins typographique, comme dans le tableau Excel

# SPEC-LFB-BAL-01 rév. C. operateur : >=, <= ou =.
EXIGENCES = [
    ("EX-01-hauteur", "Rebond", "Hauteur de lâcher", "=", 2.0, "m", "C"),
    ("EX-01-rebond", "Rebond", "Hauteur de rebond à chaque position", ">=", 135, "cm", "C"),
    ("EX-01-positions", "Rebond", "Nombre de positions (1 lâcher par position)", "=", 6, "positions", "C"),
    ("EX-02-vitesse", "Tirs répétés", "Vitesse de tir sur plaque d'acier", "=", 50, "km/h", "C"),
    ("EX-02-tirs", "Tirs répétés", "Tirs par série", ">=", 1000, "tirs", "C"),
    ("EX-02-pression", "Tirs répétés", "Pression résiduelle après chaque série (80 % de 0,8 bar)", ">=", 0.64, "bar", "C"),
    ("EX-03-duree-cycle", "Absorption d’eau", "Durée par cycle", ">=", 3, "min", "C"),
    ("EX-03-duree", "Absorption d’eau", "Durée totale (5 cycles, 250 rotations)", ">=", 15, "min", "C"),
    ("EX-03-prise-eau", "Absorption d’eau", "Prise d'eau (en % de la masse)", "<=", 10.0, "%", "C"),
    ("EX-04-palier", "Froid", "Température du palier de stockage (16 h)", "<=", -20.0, "°C", "C"),
    ("EX-04-duree", "Froid", "Durée du palier de stockage", ">=", 16, "h", "C"),
    ("EX-04-rebond", "Froid", f"Rebond à {M}5 °C (lâcher de 2,0 m)", ">=", 120, "cm", "C"),
    ("EX-05-cycles", "Usure", "Nombre de cycles réalisés", ">=", 500, "cycles", "C"),
    ("EX-05-perte", "Usure", "Perte de masse après 500 cycles", "<=", 2.0, "%", "C"),
]

# Tableau de résultats LP-500 (S-N L-0042).xlsx, ligne pour ligne.
RESULTATS = [
    ("R-P1", "EX-01", "Rebond", 141, "cm", "L-0042", "Lâcher 2,0 m ; marque légère, pas de décollement ; VF OK"),
    ("R-P2", "EX-01", "Rebond", 140, "cm", "L-0042", "VF OK"),
    ("R-P3", "EX-01", "Rebond", 140, "cm", "L-0042", "VF OK"),
    ("R-P4", "EX-01", "Rebond", 132, "cm", "L-0042", "VF OK"),
    ("R-P5", "EX-01", "Rebond", 139, "cm", "L-0042", "VF OK"),
    ("R-P6", "EX-01", "Rebond", "—", "cm", "L-0042", "Lâcher non réalisé (banc indisponible)"),
    ("T-1", "EX-02", "Tirs / pression résiduelle", "1 000 / 0,74", "tirs / bar", "L-0042", "50 km/h ; VF OK"),
    ("T-2", "EX-02", "Tirs / pression résiduelle", "1 000 / 0,72", "tirs / bar", "L-0042", "VF OK"),
    ("T-3", "EX-02", "Tirs / pression résiduelle", "750 / 0,61", "tirs / bar", "L-0042", "Arrêt anticipé (fin de journée) ; VF OK"),
    ("E-1 à E-5", "EX-03", "Durée par cycle / total", "3 / 15", "min", "L-0043", "L-0042 en usure ; aucun décollement"),
    ("E-EAU", "EX-03", "Prise d’eau", 6, "%", "L-0043", ""),
    ("F-STO", "EX-04", "Palier de stockage", -4, "°F", "L-0042", "16 h"),
    ("F-REB", "EX-04", f"Rebond à {M}5 °C", 116, "cm", "L-0042", ""),
    ("U-N", "EX-05", "Cycles réalisés", 450, "cycles", "L-0042", "Arrêt planifié, reprise semaine 46"),
    ("U-PERTE", "EX-05", "Perte de masse à 450 cycles", 1.4, "%", "L-0042", ""),
]

# Registre des non-conformités.xlsx.
NON_CONFORMITES = [
    ("NC-2025-014", "LP-400", "Tirs répétés, série 3",
     "Fuite de valve : pression résiduelle 0,58 bar (critère ≥ 0,64 bar).",
     "Valve mal collée sur la vessie.", "Nouvelle colle de valve et contrôle de la valve à 100 %. Essai repris (RA-L400-03).",
     "Clôturée", "2025-11-20"),
    ("NC-2025-021", "LP-400", "Absorption d’eau", "Prise d’eau à une couture après la pluie.",
     "Couture piquée trop perméable.", "Nouveau thermocollage des panneaux. Essai repris (RA-L400-03).", "Clôturée", "2025-11-20"),
    ("NC-2026-003", "LP-400", "Froid", "Rebond à froid 112 cm, hors critère.",
     "Lot de vessies trop rigide au froid.", "Changement de fournisseur de vessie.", "Clôturée", "2026-04-30"),
]

# Grille tarifaire 2026.xlsx (CAD, avant taxes). essai = clé utilisée par les outils.
TARIFS = [
    ("rebond", 1450, 2),
    ("tirs", 3900, 4),
    ("absorption", 1200, 1),
    ("froid", 1650, 2),
    ("usure", 6800, 30),
    ("rapport", 950, 5),
]


def creer(chemin=BASE):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    if os.path.exists(chemin):
        os.remove(chemin)
    cx = sqlite3.connect(chemin)
    cx.executescript("""
        CREATE TABLE exigences(id TEXT PRIMARY KEY, essai TEXT, parametre TEXT, operateur TEXT,
                               valeur_critere REAL, unite TEXT, revision TEXT);
        CREATE TABLE resultats(id TEXT PRIMARY KEY, exigence TEXT, parametre TEXT, valeur,
                               unite TEXT, sn TEXT, remarque TEXT);
        CREATE TABLE non_conformites(id TEXT PRIMARY KEY, produit TEXT, essai TEXT, description TEXT,
                                     cause TEXT, action TEXT, statut TEXT, date_cloture TEXT);
        CREATE TABLE tarifs(essai TEXT PRIMARY KEY, prix REAL, delai_jours INTEGER);
    """)
    cx.executemany("INSERT INTO exigences VALUES (?,?,?,?,?,?,?)", EXIGENCES)
    cx.executemany("INSERT INTO resultats VALUES (?,?,?,?,?,?,?)", RESULTATS)
    cx.executemany("INSERT INTO non_conformites VALUES (?,?,?,?,?,?,?,?)", NON_CONFORMITES)
    cx.executemany("INSERT INTO tarifs VALUES (?,?,?)", TARIFS)
    cx.commit()
    cx.close()
    return chemin


if __name__ == "__main__":
    c = creer()
    print(f"Créée : {os.path.relpath(c, RACINE)} · {len(EXIGENCES)} exigences, {len(RESULTATS)} résultats, "
          f"{len(NON_CONFORMITES)} non-conformités, {len(TARIFS)} tarifs")
