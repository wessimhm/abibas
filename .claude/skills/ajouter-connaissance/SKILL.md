---
name: ajouter-connaissance
description: "Convertit un document Word (.docx) ou Excel (.xlsx) en fiche Markdown pour la base de connaissances : titres, tableaux, virgule décimale, en-tête de traçabilité, valeurs recopiées à l’identique. Range la fiche directement dans connaissances/<dossier>/, marquée brouillon, puis un script vérifie que chaque nombre du document est dans la fiche, et rien de plus. À utiliser pour « ajoute ce document à la base », « convertis ce Word en Markdown », ou un fichier d’originaux/ qui n’a pas encore sa version .md."
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(python3 outils/lire_document.py *), Bash(python3 .claude/skills/ajouter-connaissance/scripts/verifier_conversion.py *)
---

# Ajouter un document à la base de connaissances

## Ce dossier
- `SKILL.md` : la méthode (ce fichier).
- `scripts/verifier_conversion.py` : le contrôle. **On l’exécute, on ne le lit pas.** Il compare les nombres du document d’origine et de la fiche, et compte ce qui ne se convertit pas (images, commentaires).

## La méthode
1. **Trouver le document.** Celui qu’on vous donne, ou un fichier d’`originaux/` sans fiche du même nom dans `connaissances/`. Si la fiche existe déjà, le dire et demander : nouvelle révision à remplacer, ou erreur ?
2. **Le lire** avec l’outil, jamais en devinant : `python3 outils/lire_document.py "<document>"`.
3. **Ouvrir une fiche voisine** du même dossier de `connaissances/` (par exemple PR-QUA-02 pour une procédure) et suivre sa forme.
4. **Écrire la fiche** :
   - ligne 1 : `<!-- ref: <code> rév. <X> -->`, comme les autres fiches ;
   - ligne 2 : `<!-- source : <chemin du document d’origine> -->` (le script s’en sert) ;
   - `# <titre>`, puis la ligne en italique (type, révision, date, propriétaire), telle qu’écrite ;
   - ligne suivante : `> Brouillon rédigé avec l’aide de l’IA, à vérifier.` ;
   - chaque titre du document devient `##`, chaque tableau un tableau Markdown, une ligne par ligne ;
   - une liste numérotée se renumérote 1., 2., 3. (l’outil affiche « 1. » partout : la numérotation de Word n’est pas dans le texte ; le contrôle ignore ces numéros) ;
   - un en-tête de tableau sur deux lignes (cellules fusionnées) devient une seule ligne : « Étalonnage · dernier », « Étalonnage · prochain » ;
   - un fichier Excel : une section `##` par feuille, un tableau par feuille.
5. **Recopier, ne pas réécrire.** Chaque valeur à l’identique : virgule décimale, espace des milliers, unité, date telle qu’écrite. Ne rien résumer, reformuler, convertir ni compléter. Une valeur illisible : `[À COMPLÉTER]`.
6. **Dire ce qui ne passe pas.** Là où l’outil affiche `[IMAGE NON LUE]`, écrire `[À COMPLÉTER : image non convertie, <sa légende>]`, et garder la ligne de légende telle quelle. Ne jamais décrire une image qu’on n’a pas vue.
7. **Choisir le dossier** : `1-clients` (spécifications, fiches client), `2-savoir` (produit, méthodes, rapports validés, registres, leçons), `3-processus` (procédures, modèles, plans d’essai), `4-regles` (glossaire, politiques), `5-prix` (tarifs). En cas de doute, demander.
8. **Ranger** la fiche avec Write directement dans `connaissances/<dossier>/<nom du fichier d’origine>.md` : le nom du fichier, pas le titre intérieur. Le hook `garde.py` l’accepte parce que c’est une fiche **nouvelle** ; il refuse de toucher une fiche déjà validée. Pour corriger, réécrire la fiche entière avec Write : Edit est interdit dans `connaissances/` (settings.json). Tant que la ligne « Brouillon » est là, la fiche peut encore être réécrite ; quand un humain l’a relue, il retire cette ligne et la fiche ne se modifie plus depuis l’IA.
9. **Consigner** dans `travail/DECISIONS.md` chaque choix non évident (en-tête fusionné, dossier choisi, valeur illisible), comme le demande le CLAUDE.md.

## Avant de dire « terminé »
Le contrôle se relance tout seul après l’écriture (hook). Lancer aussi :
`python3 .claude/skills/ajouter-connaissance/scripts/verifier_conversion.py "connaissances/<dossier>/<fiche>.md"`
- **Nombre manquant** : une valeur du document n’est pas dans la fiche. Corriger.
- **Nombre en trop** : une valeur de la fiche n’est pas dans le document (inventée ou convertie). Corriger.
- Tant qu’il échoue, corriger. S’il signale des images ou des commentaires, vérifier que chacun a son `[À COMPLÉTER]`.

## Rendre
En quelques lignes : le chemin de la fiche, le dossier proposé, le résultat du contrôle, la liste des `[À COMPLÉTER]`. Rappeler qu’un humain relit la fiche puis retire la ligne « Brouillon » : c’est ce geste qui la valide.
