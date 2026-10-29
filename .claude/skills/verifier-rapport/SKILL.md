---
name: verifier-rapport
description: "Vérifie un rapport d’essai complet avec quatre relecteurs en parallèle (cohérence, conformité à la spec, logique, langue) et rend un seul tableau des écarts classé par gravité (Critique, Majeur, Mineur). À utiliser quand on demande de vérifier, relire ou contrôler un rapport. Ne modifie jamais le rapport."
---

# Vérifier un rapport d’essai (orchestration)

Lecture seule : aucun relecteur ne modifie le rapport. L’ingénieure décide quoi corriger.

## La méthode
1. Identifier le rapport (par défaut : `essais/RA-L500-01 - Rapport d essai LP-500 (brouillon a verifier).md`).
2. Lancer **en parallèle**, dans un seul message, quatre sous-agents avec l’outil Agent :
   - `verificateur-coherence` : valeurs identiques au tableau de résultats et à la fiche produit, révision de la spec, S/N, durées, comptages ; il lance aussi `python3 tests/verifier_rapport.py`.
   - `verificateur-conformite` : chaque valeur contre son critère, avec le MCP `verifier_valeur` ; exigences sans résultat ; unités.
   - `relecteur-logique` : chaque conclusion découle-t-elle des résultats ? Conformité prononcée à la place de l’ingénieure ? « Sans anomalie » contredit par les données ?
   - `relecteur-langue` : orthographe, grammaire, glossaire Abibas (essai, spécimen, VF, unités, virgule décimale).
3. Attendre les quatre réponses. Fusionner les doublons : un même écart trouvé par deux relecteurs = une seule ligne, avec les deux relecteurs cités.
4. Classer par gravité :
   - **Critique** : valeur hors critère présentée comme bonne, conformité affirmée à tort, essai manquant non signalé.
   - **Majeur** : incohérence avec le tableau, la fiche produit ou la spec ; référence erronée ; déviation non déclarée ; donnée absente non marquée.
   - **Mineur** : langue, style, vocabulaire.

## Le format de sortie
Un seul tableau Markdown, trié par gravité :

| Gravité | Section | Ce qui est écrit | Le problème | Source | Trouvé par |

Puis trois lignes : le nombre d’écarts par gravité ; ce que les relecteurs n’ont pas pu vérifier ; la phrase « Décision à l’ingénieure responsable, Julie Tremblay : quels écarts confirmez-vous ? »
