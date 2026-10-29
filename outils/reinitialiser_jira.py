#!/usr/bin/env python3
"""Remet le Jira simulé (donnees/jira-simule.json) dans son état initial : QUAL-41 et QUAL-42.
Usage : python3 outils/reinitialiser_jira.py      (entre deux répétitions de la démo D10)"""
import os
import sys

for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp"))
import jira_simule_server as j  # noqa: E402

j.reinitialiser()
print(f"Jira simulé remis à zéro : {', '.join(t['cle'] for t in j.TICKETS_INITIAUX)} ({os.path.relpath(j.MAGASIN, j.RACINE)})")
