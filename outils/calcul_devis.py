#!/usr/bin/env python3
"""Raccourci : le calcul vit dans le skill devis-abibas (.claude/skills/devis-abibas/scripts/calcul_devis.py).

Usage (identique) :
    python3 outils/calcul_devis.py --essais rebond,absorption,froid --specimens 2 --delai-souhaite 15
"""
import os
import runpy
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(ICI, "..", ".claude", "skills", "devis-abibas", "scripts", "calcul_devis.py")
sys.argv[0] = SCRIPT
runpy.run_path(SCRIPT, run_name="__main__")
