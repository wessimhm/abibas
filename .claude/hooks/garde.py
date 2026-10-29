#!/usr/bin/env python3
"""Hook PreToolUse : bloque les actions à risque AVANT qu'elles aient lieu.
- Bash : suppression (rm, rmdir, del, Remove-Item, -delete, rmtree…), envoi ou réseau
  (curl, wget, mail, sendmail, scp, ftp, Invoke-WebRequest).
- Write / Edit : toute écriture dans connaissances/ (la base de connaissances), originaux/ (les Word et Excel d’origine), essais/ (les
  données d'essai brutes) ou donnees/ (la base de données du labo). Ces dossiers se lisent, ils ne se modifient pas depuis l'IA.
Code 2 = action bloquée ; le message (stderr) est renvoyé à Claude."""
import json
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
PROTEGES = {"connaissances", "originaux", "essais", "donnees"}

if outil == "Bash":
    cmd = entree.get("command", "")
    if re.search(SUPPRESSION_ENVOI, cmd, re.I):
        print("Bloqué par la règle d'équipe (Politique IA et confidentialité) : pas de suppression "
              "ni d'envoi depuis l'IA. Demandez à l'ingénieur de le faire lui-même.", file=sys.stderr)
        sys.exit(2)
elif outil in ("Write", "Edit", "MultiEdit"):
    chemin = entree.get("file_path", "")
    parties = [p.lower() for p in re.split(r"[\\/]", chemin)]
    if PROTEGES & set(parties):
        print("Bloqué : connaissances/, originaux/, essais/ et donnees/ sont en lecture seule. Écrivez dans travail/.", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
