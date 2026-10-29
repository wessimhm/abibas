---
name: rapport-essai
description: "Rédige un rapport d’essai LP-500 (ou une section Résultats) au format du modèle de rapport Abibas, à partir du tableau de résultats et de SPEC-LFB-BAL-01 rév. C. À utiliser dès qu’on demande de rédiger, refaire, corriger ou compléter un rapport d’essai ou une section Résultats."
---

# Rédiger un rapport d’essai LP-500

## Les sources (et seulement elles)
- Valeurs mesurées : `essais/Tableau de résultats LP-500 (S-N L-0042).md`
- Exigences : `connaissances/1-clients/SPEC-LFB-BAL-01 rev C - Specification ballon.md`
- Format : `connaissances/3-processus/Modele de rapport d essai.md` ; exemple de style : `connaissances/2-savoir/RA-L400-03 - Rapport d essai LP-400 (exemple valide).md`
- Fiche produit : `connaissances/2-savoir/Fiche produit LP-500.md`
- Vocabulaire et unités : `connaissances/4-regles/Glossaire et regles de redaction.md`
- Utile : leçons apprises (LA-07, LA-09, LA-11, LA-12) et registre des non-conformités.

## La méthode
1. Lire les sources avant d’écrire quoi que ce soit.
2. Suivre le modèle : 1 Objet, 2 Spécimen, 3 Résultats par exigence (EX-01 à EX-05), 4 Déviations, 5 Conclusion, Signatures.
3. Pour chaque exigence : conditions, tableau des valeurs avec le critère, écarts, statut « à valider ».
4. Comparer chaque valeur à son critère avec l’outil MCP `verifier_valeur`, jamais de tête.
5. Signaler chaque écart en une phrase factuelle : valeur hors critère, durée trop courte, spécimen différent, unité différente, essai incomplet.
6. Donnée absente : **[À COMPLÉTER]**. Ne jamais supposer une valeur.
7. Une valeur en °F dans le tableau : ne pas la recopier, signaler l’unité à corriger.
8. Conclusion : résumer les écarts et renvoyer la décision à Julie Tremblay. Interdit : « conforme », « qualifié », « sans anomalie ».
9. Marquer le document : « Brouillon rédigé avec l’aide de l’IA, à vérifier ».

## Le format de sortie
- Fichier Markdown dans `travail/`, nommé `travail/RA-L500-01.md` (ou le numéro demandé).
- Spécification citée avec sa révision : « SPEC-LFB-BAL-01 rév. C ».
- Pour une version Word : `python3 outils/md_vers_docx.py travail/RA-L500-01.md`.

## Avant de dire « terminé »
Le test se relance tout seul après chaque écriture (hook). Lancer aussi `python3 tests/verifier_rapport.py travail/RA-L500-01.md`. Tant qu’il échoue, corriger, ou expliquer à l’ingénieure ce qui reste [À COMPLÉTER].
