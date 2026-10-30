#!/usr/bin/env python3
"""Hook PostToolUse (Write, Edit) : après chaque modification dans travail/ ou connaissances/,
relance automatiquement le test déterministe qui correspond :
- un rapport (travail/RA-*.md ou .docx) : tests/verifier_rapport.py ;
- une offre (travail/offre*.md ou .docx) : tests/verifier_devis.py ;
- une fiche de connaissance ajoutée (connaissances/…/*.md) : le contrôle du skill ajouter-connaissance.
S'il échoue, code 2 : le résultat est montré à Claude, qui doit corriger."""
import json
import os
import subprocess
import sys

try:
    d = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
except Exception:
    sys.exit(0)
chemin = (d.get("tool_input", {}) or {}).get("file_path", "")
racine = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
norm = chemin.replace("\\", "/")
nom = os.path.basename(norm).lower()
if "/connaissances/" in "/" + norm and nom.endswith(".md"):
    test = os.path.join(".claude", "skills", "ajouter-connaissance", "scripts", "verifier_conversion.py")
elif "/travail/" not in "/" + norm or not nom.endswith((".md", ".docx")):
    sys.exit(0)
elif nom.startswith("ra-"):
    test = "verifier_rapport.py"
elif nom.startswith("offre"):
    test = "verifier_devis.py"
else:
    sys.exit(0)

env = dict(os.environ, PYTHONIOENCODING="utf-8")
script = os.path.join(racine, test) if os.sep in test or "/" in test else os.path.join(racine, "tests", test)
r = subprocess.run([sys.executable, script, chemin],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=racine, env=env)
test = os.path.basename(test)
if r.returncode != 0:
    echecs = "\n".join(l for l in r.stdout.splitlines() if l.startswith(("FAIL", "RÉSULTAT", "ERREUR")))
    print(f"Test automatique après modification ({test}) : échec.\n" + echecs, file=sys.stderr)
    sys.exit(2)
print(f"Test automatique après modification ({test}) : tous les contrôles passent.")
sys.exit(0)
