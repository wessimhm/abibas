---
name: devis-abibas
description: "Prépare une offre d’essais Abibas à partir d’une demande client et de la grille tarifaire 2026 : calcul par script (jamais de tête), règles du spécimen supplémentaire (+35 %) et de l’urgence (+20 % seulement sous 10 jours ouvrables), rédaction au format du modèle d’offre. À utiliser pour toute demande de devis, d’offre ou de prix."
---

# Préparer une offre d’essais

## Les sources
- La demande : par exemple `base-abibas/texte/1-clients/Courriel Ligue de foot de Belmont - demande offre serie 2.md`.
- Les prix : `base-abibas/5-prix/Grille tarifaire 2026.xlsx` (texte : `base-abibas/texte/5-prix/Grille tarifaire 2026.md`).
- Le format : `base-abibas/texte/3-processus/Modele d offre.md`.
- La spec citée : SPEC-LFB-BAL-01 rév. C (LA-11 : la révision exacte).

## La méthode
1. Lire la demande et en extraire : les essais demandés, le nombre de spécimens, le délai souhaité (3 semaines = 15 jours ouvrables).
2. **Calculer avec le script, jamais de tête** :
   `python3 outils/calcul_devis.py --essais rebond,absorption,froid --specimens 2 --delai-souhaite 15`
   Si le serveur MCP `verifier-valeur` est branché, recouper avec l’outil `calculer_devis` (mêmes entrées). Les deux totaux doivent être identiques ; sinon, s’arrêter et le dire.
3. Appliquer les règles telles que le script les calcule :
   - spécimen supplémentaire : +35 % du prix de chaque essai, par spécimen en plus ;
   - urgence : +20 % sur le total **seulement** si les résultats sont demandés en moins de 10 jours ouvrables. « Prioritaire » ou « rapidement » ne suffisent pas : on compare des jours ;
   - prix avant taxes, taxes en sus, validité 30 jours.
4. Rédiger l’offre au format du modèle dans `travail/offre-<nom>.md`, avec le détail du calcul et le délai.
5. Marquer l’offre « Brouillon préparé avec l’aide de l’IA, à valider par le chargé de projet avant envoi ». Ne rien envoyer : Karim Haddad valide et envoie.

## Avant de dire « terminé »
Le test se relance tout seul après l’écriture (hook). Lancer aussi `python3 tests/verifier_devis.py travail/offre-<nom>.md`. Tant qu’il échoue, corriger.
