---
description: Vérifie un rapport d'essai avec les quatre relecteurs en parallèle, puis le test déterministe
argument-hint: "[rapport, par exemple RA-L500-01]"
---

Vérifie le rapport $ARGUMENTS (dans `essais/texte/` ou `travail/` ; par défaut le brouillon RA-L500-01) avec le skill `verifier-rapport` :

1. Lance en parallèle, dans un seul message, les quatre relecteurs : verificateur-coherence, verificateur-conformite, relecteur-logique, relecteur-langue.
2. Fusionne leurs remontées en un seul tableau, classé par gravité (Critique, Majeur, Mineur), sans doublon.
3. Lance `python3 tests/verifier_rapport.py` sur le rapport et ajoute le résultat sous le tableau.
4. Ne modifie aucun fichier et ne prononce aucune conformité : c'est l'ingénieure responsable, Julie Tremblay, qui décide.
