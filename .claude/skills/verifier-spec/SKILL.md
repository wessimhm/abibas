---
name: verifier-spec
description: "Vérifie chaque valeur d’un rapport ou d’un tableau de résultats contre les critères de SPEC-LFB-BAL-01 rév. C, avec l’outil MCP verifier_valeur. À utiliser pour tout contrôle chiffré (rebond, tirs, pression, prise d’eau, perte de masse, cycles). Ne modifie rien."
---

# Vérifier un document contre la spécification

Lecture seule : ce skill ne modifie aucun fichier et ne prononce aucune conformité.

## La méthode
1. Lister les critères avec l’outil MCP `lister_exigences`.
2. Pour chaque valeur chiffrée du document, appeler `verifier_valeur(exigence, valeur_mesuree, unite)`. Exemples : `EX-01-rebond`, `EX-02-tirs` (750 tirs), `EX-02-pression` (0,61 bar = 0.61), `EX-03-prise-eau`, `EX-04-rebond`, `EX-05-cycles`. Ne jamais comparer de tête.
3. Contrôler aussi ce qui manque : chaque exigence a-t-elle un résultat ? (position P6, EX-05 à 450 cycles.)
4. Contrôler le spécimen : S/N L-0042 partout ? Sinon, déviation.
5. Une unité refusée (°F) : la signaler, ne pas convertir en silence.

## Le format de sortie
Un tableau Markdown : Exigence | Valeur dans le document | Critère de la spec | Résultat de l’outil | Remarque.
Puis une phrase : nombre de valeurs hors critère, nombre d’exigences sans résultat, unités à corriger.
