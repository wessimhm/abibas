#!/usr/bin/env python3
"""Hook Stop : empêche Claude de dire « terminé » tant que le test du rapport échoue.
Ne s'applique que si un rapport existe dans travail/ (RA-*.md ou RA-*.docx) : on teste le plus récent.
Pour éviter une boucle sans fin, si Claude a déjà été relancé une fois par ce hook
(stop_hook_active), on le laisse s'arrêter."""
import glob
import json
import os
import subprocess
import sys

try:
    d = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
except Exception:
    sys.exit(0)
if d.get("stop_hook_active"):
    sys.exit(0)
racine = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
rapports = [f for motif in ("RA-*.md", "RA-*.docx", "ra-*.md", "ra-*.docx")
            for f in glob.glob(os.path.join(racine, "travail", motif))]
if not rapports:
    sys.exit(0)
dernier = max(set(rapports), key=os.path.getmtime)
env = dict(os.environ, PYTHONIOENCODING="utf-8")
r = subprocess.run([sys.executable, os.path.join(racine, "tests", "verifier_rapport.py"), dernier],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=racine, env=env)
if r.returncode != 0:
    echecs = "\n".join(l for l in r.stdout.splitlines() if l.startswith(("FAIL", "RÉSULTAT", "ERREUR")))
    print(f"Pas encore terminé : le test de {os.path.basename(dernier)} échoue. Corrige, ou explique "
          "à l'ingénieure ce qui reste [À COMPLÉTER].\n" + echecs, file=sys.stderr)
    sys.exit(2)
sys.exit(0)
