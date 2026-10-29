---
name: planifier-rapport
description: "Établit le plan d’un rapport d’essai LP-500 (sections, sources, vérifications, questions ouvertes) avant toute rédaction, et le soumet à l’ingénieure pour validation. À utiliser au début d’une demande de rapport, avant d’écrire."
---

# Planifier un rapport d’essai

Ne rien rédiger à cette étape : produire un plan, puis s’arrêter pour validation.

## Le plan contient
1. **Le but** du rapport, en une phrase.
2. **Les sources** utilisées (fichiers de `base-abibas/texte/` et `essais/texte/`) et celles qui manquent.
3. **Les sections** prévues, selon le modèle de rapport : Objet, Spécimen, Résultats (EX-01 à EX-05), Déviations, Conclusion, Signatures.
4. **Pour chaque exigence** : le critère de SPEC-LFB-BAL-01 rév. C, la méthode (MET-01 à MET-05), les lignes du tableau concernées.
5. **Les vérifications prévues** : quels appels à `verifier_valeur`, quel test final (`tests/verifier_rapport.py`).
6. **Les questions ouvertes** pour l’ingénieure : données absentes (position P6, cycles restants d’EX-05), déviations (série T-3 à 750 tirs, spécimen S/N L-0043, unité °F), accord écrit du client.

## La fin de l’étape
Présenter le plan en liste numérotée, puis demander : « Validez-vous ce plan, ou que faut-il changer ? » Attendre la réponse avant de rédiger.
