#!/usr/bin/env python3
"""Hook PreToolUse : bloque les actions à risque AVANT qu'elles aient lieu.
- Bash : suppression (rm, rmdir, del, Remove-Item, -delete, rmtree…), envoi ou réseau
  (curl, wget, mail, sendmail, scp, ftp, Invoke-WebRequest).
- Write / Edit : toute écriture dans connaissances/ (la base de connaissances), SAUF une fiche nouvelle
  ou encore marquée « Brouillon rédigé avec l’aide de l’IA » (skill ajouter-connaissance) ; et dans originaux/ (les Word et Excel d’origine), entrees/ (courriels et signalements reçus), essais/ (les
  données d'essai brutes) ou donnees/ (la base de données du labo). Ces dossiers se lisent, ils ne se modifient pas depuis l'IA.
Code 2 = action bloquée ; le message (stderr) est renvoyé à Claude."""
import json
import os
import re
import sys

try:
    d = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
except Exception:
    sys.exit(0)
outil = d.get("tool_name", "")
entree = d.get("tool_input", {}) or {}

SUPPRESSION_ENVOI = (r"(^|[\s;&|(`])(rm|rmdir|del|erase|rd|Remove-Item|unlink|shred|curl|wget|mail|sendmail|"
                     r"mutt|scp|sftp|ftp|Invoke-WebRequest|Invoke-RestMethod|Send-MailMessage)(\s|$)"
                     r"|\s-delete\b|rmtree|os\.remove|os\.unlink|\.unlink\(")
PROTEGES = {"connaissances", "originaux", "entrees", "essais", "donnees"}

if outil == "Bash":
    cmd = entree.get("command", "")
    if re.search(SUPPRESSION_ENVOI, cmd, re.I):
        print("Bloqué par la règle d'équipe (Politique IA et confidentialité) : pas de suppression "
              "ni d'envoi depuis l'IA. Demandez à l'ingénieur de le faire lui-même.", file=sys.stderr)
        sys.exit(2)
elif outil in ("Write", "Edit", "MultiEdit"):
    chemin = entree.get("file_path", "")
    parties = [p.lower() for p in re.split(r"[\\/]", chemin)]
    if "connaissances" in parties and not (PROTEGES - {"connaissances"}) & set(parties) and chemin.lower().endswith(".md"):
        # La base accepte une fiche NOUVELLE, ou une fiche encore en brouillon IA (pas encore relue).
        # Une fiche relue (sans la ligne « Brouillon ») ne se modifie plus depuis l'IA.
        racine = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        complet = chemin if os.path.isabs(chemin) else os.path.join(racine, chemin)
        if not os.path.exists(complet):
            sys.exit(0)
        try:
            contenu = open(complet, encoding="utf-8").read()
        except OSError:
            contenu = ""
        if re.search(r"Brouillon rédigé avec l.aide de l.IA", contenu):
            sys.exit(0)
        print("Bloqué : cette fiche de connaissances/ a été relue et validée ; l'IA ne la modifie plus. "
              "L'IA peut seulement AJOUTER une nouvelle fiche (skill ajouter-connaissance). "
              "Pour changer une fiche validée, demandez à l'ingénieure responsable.", file=sys.stderr)
        sys.exit(2)
    if PROTEGES & set(parties):
        print("Bloqué : originaux/, entrees/, essais/ et donnees/ sont en lecture seule (et connaissances/ n’accepte que des fiches .md nouvelles). Écrivez dans travail/.", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
