#!/usr/bin/env python3
"""Remet le dépôt comme au premier jour, avant les démos : comme si on venait de le cloner.

Usage :
    python3 outils/reinitialiser_demo.py          # montre ce qui serait remis à zéro, sans rien toucher
    python3 outils/reinitialiser_demo.py --oui    # le fait

Ce qui est remis à zéro :
- les fichiers suivis par Git qui ont été modifiés (Jira simulé, base du labo, fiches…) : version d'origine ;
- les fichiers ajoutés depuis le clonage (fiche PR-LAB-04 dans connaissances/, skill créé en D3…) : supprimés ;
- tout ce qui est dans travail/ (sauf .gitkeep), journal-essais.md, donnees/journal-mcp.log ;
- .claude/settings.local.json (les « ne plus demander » accordés pendant les démos) : supprimé.
Ce qui n'est PAS touché : l'historique Git, les commits, ce qui est hors du dépôt (plugins installés,
tickets créés dans un vrai Jira, connexion au MCP Atlassian).
Réservé au formateur : c'est une suppression, décidée par un humain."""
import os
import shutil
import subprocess
import sys

for _flux in (sys.stdout, sys.stderr):  # Windows : affichage UTF-8
    try:
        _flux.reconfigure(encoding="utf-8")
    except Exception:
        pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAIRE = "--oui" in sys.argv[1:]


def git(*args):
    r = subprocess.run(["git", *args], cwd=RACINE, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f"git {' '.join(args)} a échoué")
    return r.stdout


try:
    git("rev-parse", "--is-inside-work-tree")
except Exception:
    print("ERREUR : ce dossier n'est pas un dépôt Git. Re-clonez le dépôt (ou re-décompressez le zip) pour repartir de zéro.")
    sys.exit(1)

# -z : noms avec espaces ou accents (« PR-LAB-04 - Etalonnage des instruments.md ») sans guillemets
modifies = [e[3:] for e in git("status", "--porcelain", "-z", "--untracked-files=no").split("\0") if e.strip()]
ajoutes = [e for e in git("ls-files", "-z", "--others", "--exclude-standard").split("\0") if e.strip()]
ignores_a_vider = []
dossier_travail = os.path.join(RACINE, "travail")
if os.path.isdir(dossier_travail):
    ignores_a_vider += [os.path.join("travail", n) for n in sorted(os.listdir(dossier_travail)) if n != ".gitkeep"]
for f in ["journal-essais.md", os.path.join("donnees", "journal-mcp.log"), os.path.join(".claude", "settings.local.json")]:
    if os.path.exists(os.path.join(RACINE, f)):
        ignores_a_vider.append(f)
a_supprimer = sorted(set(ajoutes) | set(ignores_a_vider))

if not modifies and not a_supprimer:
    print("Rien à faire : le dépôt est déjà dans son état de départ.")
    sys.exit(0)

print("Fichiers modifiés, remis dans leur version d'origine :" if modifies else "Aucun fichier modifié.")
for f in modifies:
    print(f"  ↺ {f}")
print("Fichiers ajoutés pendant les démos, supprimés :" if a_supprimer else "Aucun fichier ajouté.")
for f in a_supprimer:
    print(f"  ✕ {f}")

if not FAIRE:
    print("\nRien n'a été touché. Pour le faire : python3 outils/reinitialiser_demo.py --oui")
    sys.exit(0)

if modifies:
    git("checkout", "HEAD", "--", *modifies)
for f in a_supprimer:
    chemin = os.path.join(RACINE, f)
    if os.path.isdir(chemin) and not os.path.islink(chemin):
        shutil.rmtree(chemin)
    elif os.path.exists(chemin) or os.path.islink(chemin):
        os.remove(chemin)
# dossiers devenus vides (par exemple un skill créé puis supprimé)
for f in a_supprimer:
    d = os.path.dirname(os.path.join(RACINE, f))
    while d.startswith(RACINE) and d != RACINE and os.path.isdir(d) and not os.listdir(d):
        os.rmdir(d)
        d = os.path.dirname(d)

reste = git("status", "--porcelain").strip()
print(f"\nFait : {len(modifies)} fichier(s) remis d'origine, {len(a_supprimer)} supprimé(s).")
print("Le dépôt est comme au premier jour." if not reste else "Attention, il reste :\n" + reste)
print("Hors du dépôt, à faire à la main si besoin : /clear dans Claude Code ; désinstaller les plugins "
      "ajoutés (/plugin) ; supprimer dans Jira les tickets créés en E6.")
