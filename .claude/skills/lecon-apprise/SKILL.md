---
name: lecon-apprise
description: "Transforme une non-conformité clôturée du registre des NC en leçon apprise, au format du registre des leçons apprises (N°, date, leçon, origine, ce que l’on fait maintenant). Vérifie d’abord que la NC est clôturée et qu’aucune leçon ne la cite déjà, recopie les faits sans rien inventer, et rend une ligne brouillon dans travail/ que Sofia Benali ajoute au registre. À utiliser pour « tire une leçon de NC-… », « ajoute une leçon apprise », « capitalise cette non-conformité », ou après la clôture d’une NC."
allowed-tools: Read, Grep, Glob, Write, mcp__verifier-valeur__chercher_nc, Bash(python3 .claude/skills/lecon-apprise/scripts/verifier_lecon.py *)
---

# D’une non-conformité clôturée à une leçon apprise

## Ce dossier
- `SKILL.md` : la méthode (ce fichier).
- `scripts/verifier_lecon.py` : le contrôle. On l’exécute, on ne le lit pas. Il compare la ligne rédigée à la NC du registre.

## Les sources
- La NC : `connaissances/2-savoir/Registre des non-conformites.md`, ou l’outil MCP `chercher_nc` avec son numéro.
- Le format et les leçons existantes : `connaissances/2-savoir/Lecons apprises.md`. Exemple à suivre : LA-07, tirée de NC-2025-014.

## Pourquoi ces précautions
Le registre des leçons est relu avant chaque campagne. Une leçon fausse ou gonflée y fait plus de dégâts qu’une leçon absente. La leçon dit donc seulement ce que la NC établit. Le registre est un document validé, tenu par Sofia Benali : l’IA ne l’écrit pas (le hook `garde.py` le bloquerait). Elle prépare une ligne, et Sofia Benali l’ajoute.

## La méthode
1. **Trouver la NC** par son numéro (NC-AAAA-NNN). Sans numéro, lister les NC clôturées qu’aucune leçon ne cite, et demander laquelle traiter.
2. **Vérifier qu’elle est clôturée.** Une NC ouverte n’a ni cause ni action confirmées : s’arrêter et le dire.
3. **Vérifier qu’aucune leçon ne la cite déjà**, dans la colonne Origine du registre des leçons (par exemple NC-2025-014 → LA-07). Si une leçon existe, le dire et ne rien rédiger.
4. **Rédiger une seule ligne**, avec les cinq colonnes du registre :
   - **N°** : `[À COMPLÉTER]`. Le registre est un extrait, d’où les trous (LA-03, LA-05…). Le numéro suivant n’est pas déductible : Sofia Benali l’attribue. Indiquer sous le tableau le dernier numéro visible.
   - **Date** : le mois et l’année de la clôture de la NC, au format du registre (« novembre 2025 » pour une clôture le 20 novembre 2025). C’est la seule mise en forme permise, et elle se déclare sous le tableau.
   - **Leçon** : une ou deux phrases courtes, à l’impératif ou à l’infinitif, comme « Toujours aller au bout des 1 000 tirs par série. » Elle généralise le fait de la NC en règle de travail. Elle n’ajoute ni cause, ni chiffre, ni produit que la NC ne contient pas.
   - **Origine** : le numéro de la NC, puis entre parenthèses le produit, l’essai et la valeur du constat, recopiés à l’identique (modèle : « NC-2025-014 (LP-400, tirs répétés série 3, pression résiduelle 0,58 bar) »).
   - **Ce que l’on fait maintenant** : l’action corrective de la NC, telle qu’écrite. Si elle ne dit rien de ce que le labo fait désormais en routine, écrire `[À COMPLÉTER]` plutôt qu’inventer une pratique.
5. **Respecter le glossaire** : essai, spécimen, °C, virgule décimale, une espace avant l’unité. Ne jamais écrire « conforme », « non conforme » ou « qualifié » : ces mots sont réservés à Julie Tremblay. Une valeur s’écrit « hors critère ».
6. **Écrire** `travail/lecon-<NC>.md` (par exemple `travail/lecon-NC-2025-021.md`) au format ci-dessous.
7. **Consigner** dans `travail/DECISIONS.md` chaque choix non évident (formulation généralisée, action sans pratique de routine…).

## Le format de sortie

```markdown
# Leçon apprise proposée · <NC>

> Brouillon rédigé avec l’aide de l’IA, à vérifier.

| N° | Date | Leçon | Origine | Ce que l’on fait maintenant |
|---|---|---|---|---|
| [À COMPLÉTER] | <mois année> | <leçon> | <NC> (<produit>, <essai>, <constat>) | <action> |

- Source : `connaissances/2-savoir/Registre des non-conformites.md`, ligne <NC> (clôturée le <date telle qu’écrite>).
- N° : à attribuer par Sofia Benali (dernier numéro visible dans l’extrait : <LA-xx>).
- Date : mois de clôture de la NC, au format du registre.
- À relire par Sofia Benali, qui ajoute la ligne au registre des leçons apprises.
```

## Avant de dire « terminé »
Lancer `python3 .claude/skills/lecon-apprise/scripts/verifier_lecon.py travail/lecon-<NC>.md`. Il vérifie :
- la NC existe, elle est clôturée, et aucune leçon ne la cite déjà ;
- la date correspond au mois de clôture ;
- l’origine cite la NC ;
- aucun nombre de la ligne n’est absent de la NC ;
- la mention « Brouillon » est présente, et la conformité n’est pas prononcée.

Tant qu’il échoue, corriger.

## Rendre
En quelques lignes : le chemin du fichier, la ligne proposée, le résultat du contrôle et les `[À COMPLÉTER]`. Rappeler que Sofia Benali attribue le numéro et ajoute la ligne au registre.
