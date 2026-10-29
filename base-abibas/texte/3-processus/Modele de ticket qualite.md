<!-- ref: MOD-TQ rév. A -->
# Modèle de ticket qualité · Jira, projet QUAL
_Qualité et certification Abibas Sport · Un ticket par réclamation client · rév. A, septembre 2026_

## 1. Quand créer un ticket

- Un ticket qualité est créé pour chaque **réclamation client** : un produit livré qui ne fonctionne pas comme prévu.
- Pas de ticket pour une question commerciale, une facture, une demande d’offre ou un remerciement.
- Avant de créer, chercher les cas semblables : tickets QUAL existants et registre des non-conformités.

## 2. Les champs obligatoires

| Champ | Contenu attendu | Exemple |
|---|---|---|
| Projet | Toujours QUAL | QUAL |
| Type | Réclamation client | Réclamation client |
| Résumé | 80 caractères au maximum : client · produit ou unité · symptôme | Belmont · ballon 15 · couture qui prend l’eau |
| Client | Nom du client et programme | Ligue de foot de Belmont, saison 2027 |
| Produit | Produit concerné | Ballon LP-500 |
| S/N | Numéro de série complet | S/N L-0042 |
| Symptôme | Ce que le client observe, avec ses mots | Ballon dégonflé, couture ouverte |
| Date de l’incident | Date ou événement déclencheur | 24 octobre 2026 |
| Nombre d’unités touchées | Un nombre, avec la liste des unités | 1 (ballon 15) |
| Gravité proposée | Critique / Majeure / Mineure, toujours suivie de « à confirmer » | Mineure, à confirmer |
| Exigence possiblement touchée | Exigence de la spécification client | EX-03 (absorption d’eau) |
| Cas semblables | Tickets QUAL et NC liés | NC-2025-021 |
| Pièces jointes | Photos, journaux, courriel d’origine | photo.jpg |
| Statut | Toujours « À trier » à la création | À trier |
| Étiquette | « cree-par-IA » si le ticket est créé par un agent | cree-par-IA |
| Demandeur | La personne qui signale | Isabelle Roy |

## 3. Les règles

- La gravité est **proposée**, jamais décidée : Julie Tremblay la confirme au tri.
- Le statut est toujours « À trier » à la création. Seul un humain change le statut.
- La réponse au client est un **brouillon**. Karim Haddad la relit et l’envoie.
- Le ticket ne contient aucune cause supposée : seulement les faits du client et les cas semblables.

_Document fictif de formation._
