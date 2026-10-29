---
name: devis-abibas
description: "Prépare une offre d’essais Abibas à partir d’une demande client et de la grille tarifaire 2026 : calcul par script (jamais de tête), spécimen supplémentaire (+35 %), urgence (+20 % seulement sous 10 jours ouvrables), rédaction au format du gabarit d’offre. À utiliser pour toute demande de devis, d’offre ou de prix."
allowed-tools: Read, Grep, Bash(python3 .claude/skills/devis-abibas/scripts/calcul_devis.py *)
---

# Préparer une offre d’essais

## Ce dossier
- `SKILL.md` : la méthode (ce fichier).
- `scripts/calcul_devis.py` : le calcul. **On l’exécute, on ne le lit pas.**
- `references/cas-particuliers.md` : les cas qui sortent de l’ordinaire. À lire seulement si la demande parle de délai court, de « prioritaire », de spécimens en plus ou d’essais non demandés.
- `assets/gabarit-offre.md` : le gabarit à remplir. On le copie dans `travail/`, on ne le modifie pas.

## La méthode
1. Lire la demande (par exemple `entrees/courriels/Courriel Ligue de Belmont - demande offre serie 2.md`) : essais demandés, nombre de spécimens, délai souhaité en jours ouvrables.
2. Si un point n’est pas simple, lire `references/cas-particuliers.md`.
3. **Calculer avec le script, jamais de tête** :
   `python3 .claude/skills/devis-abibas/scripts/calcul_devis.py --essais rebond,absorption,froid --specimens 2 --delai-souhaite 15`
   Si le serveur MCP `verifier-valeur` est branché, recouper avec l’outil `calculer_devis`. Les deux totaux doivent être identiques ; sinon, s’arrêter et le dire.
4. Copier `assets/gabarit-offre.md` dans `travail/offre-<nom>.md` et remplir chaque champ avec les sorties du script. Citer SPEC-LFB-BAL-01 rév. C.
5. Marquer l’offre « Brouillon préparé avec l’aide de l’IA, à valider par le chargé de projet avant envoi ». Ne rien envoyer : Karim Haddad valide et envoie.

## Avant de dire « terminé »
Le test se relance tout seul après l’écriture (hook). Lancer aussi `python3 tests/verifier_devis.py travail/offre-<nom>.md`. Tant qu’il échoue, corriger.
