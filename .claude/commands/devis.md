---
description: Prépare une offre d'essais à partir d'un courriel client et de la grille tarifaire 2026
argument-hint: "[courriel, par exemple « Courriel Ligue de Belmont - demande offre serie 2 »]"
---

Prépare l'offre pour la demande $ARGUMENTS (dans `entrees/courriels/` ; par défaut le courriel série 2 de la Ligue de foot de Belmont) avec le skill `devis-abibas` :

1. Lis le courriel : essais demandés, nombre de spécimens, délai souhaité en jours ouvrables.
2. Calcule avec le script du skill, `python3 .claude/skills/devis-abibas/scripts/calcul_devis.py` (jamais de tête). Si le MCP est disponible, recoupe avec l'outil `calculer_devis`.
3. Rédige l'offre à partir du gabarit du skill (`.claude/skills/devis-abibas/assets/gabarit-offre.md`) dans `travail/offre-serie-2.md` (ou un nom adapté).
4. Lance `python3 tests/verifier_devis.py travail/offre-serie-2.md`.
5. Marque l'offre comme brouillon IA à valider par Karim Haddad. N'envoie rien.
