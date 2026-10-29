# Le harness d’Abibas Sport

Abibas Sport est une PME **fictive** de Montréal qui conçoit des ballons de foot. Elle veut faire entrer l’IA dans son travail : qualifier son ballon de match LP-500 pour la Ligue de foot de Belmont (fictive), rédiger et vérifier les rapports d’essai, préparer les offres, traiter les réclamations.

Ce dépôt contient **tout ce qu’Abibas a préparé pour travailler avec Claude**. Un nouvel ingénieur le clone, ouvre Claude Code dans le dossier, et il a d’un coup le contexte, les règles, les méthodes, les coéquipiers et les freins de l’équipe.

> Support de la formation IA d’e2ip (vendredi 2). Tout est fictif : entreprise, client, produit, personnes, chiffres. Aucune donnée client, aucune norme sous licence.

## La carte du dépôt

```text
abibas/
├── CLAUDE.md                 le carnet de bord : lu à chaque session
├── .claude/
│   ├── rules/                des règles ciblées : chargées seulement quand on touche certains fichiers
│   ├── skills/               les savoir-faire : chargés quand la tâche correspond
│   ├── commands/             les raccourcis : /verifier, /devis, /ticket
│   ├── agents/               les coéquipiers spécialisés, chacun avec ses outils
│   ├── hooks/                les freins automatiques
│   └── settings.json         les permissions : autorisé, interdit, demander
├── .mcp.json                 les connexions MCP : Jira (Atlassian) et les outils maison
├── mcp/                      le code des serveurs MCP
├── connaissances/            la base de connaissances, en Markdown : ce que l’IA lit
├── originaux/                les mêmes documents en Word et Excel, pour les humains
├── entrees/                  ce qui arrive et doit être traité : courriels, portail client, résultats
├── essais/                   l’essai en cours : le tableau de résultats et le brouillon à vérifier
├── donnees/                  la base du labo (SQLite), le Jira simulé et l’import Jira de test
├── outils/                   les petits scripts : lire un .docx, calculer un devis…
├── tests/                    les vérifications automatiques
└── travail/                  le seul endroit où Claude écrit
```

## Le rangement : chaque fichier à sa place

Quatre questions suffisent pour savoir où ranger un fichier :

| Le fichier… | Il va dans | Exemple |
|---|---|---|
| reste vrai demain (une règle, une méthode, une spec) | `connaissances/`, en Markdown | le glossaire, la fiche client |
| vient d’arriver et doit être traité | `entrees/` | un courriel, un signalement |
| est un chiffre qu’on filtre ou qu’on compare | `donnees/`, via un MCP | les résultats d’essai, les tickets |
| est produit par l’IA | `travail/` | un rapport, une offre, un ticket |

Un courriel n’entre jamais dans la base : il arrive dans `entrees/`, on le traite, et seul ce qu’il décide (un accord, un nouveau contact) est reporté dans la fiche client.

## Chaque pièce, en une phrase

| Pièce | Ce que c’est | Quand Claude la lit | Exemple chez Abibas |
|---|---|---|---|
| `CLAUDE.md` | Le carnet de bord de l’équipe | Au début de chaque session | « Jamais de conformité prononcée par l’IA » |
| `.claude/rules/` | Des règles qui ne servent que pour certains fichiers | Quand Claude lit ou écrit un fichier qui correspond | `redaction-rapports.md` : le glossaire, seulement pour les rapports |
| `.claude/skills/` | Une méthode de travail rangée dans un dossier | Quand la demande correspond à sa description | `devis-abibas` : comment faire une offre, calcul par script |
| `.claude/commands/` | Un raccourci qu’on tape | Quand on tape `/nom` | `/verifier RA-L500-01` |
| `.claude/agents/` | Un coéquipier spécialisé, avec ses seuls outils | Quand Claude lui confie une tâche | `relecteur-langue` : lecture seule |
| `.claude/hooks/` | Un frein qui s’exécute tout seul | Avant ou après chaque action | `garde.py` bloque « supprime le dossier travail » |
| `.claude/settings.json` | Les permissions | Tout le temps | `rm` interdit, écriture seulement dans `travail/` |
| `.mcp.json` + `mcp/` | Les outils branchés à Claude : Jira (Atlassian) et les outils maison | Quand Claude en a besoin | `searchJiraIssuesUsingJql` cherche dans Jira ; `verifier_valeur` compare une mesure à la spec |
| `tests/` | Les vérifications automatiques | Quand on les lance | `verifier_rapport.py` : 25 contrôles |

## CLAUDE.md : le carnet de bord

Un fichier en Markdown, à la racine, que Claude lit au début de **chaque** session. On y met ce que tout nouveau coéquipier devrait savoir dès le premier jour : le contexte, où sont les fichiers, les règles de l’équipe, les outils à utiliser. On le garde court (moins de 200 lignes) ; le détail va dans les règles, les skills ou la base.

## Les rules : des règles ciblées

Des fichiers Markdown dans `.claude/rules/`. Sans en-tête, une règle est lue à chaque session, comme le CLAUDE.md. Avec un en-tête `paths`, elle n’est lue **que** quand Claude ouvre ou écrit un fichier qui correspond : la fenêtre de contexte reste légère.

```markdown
---
paths:
  - "travail/**/*.md"
---
# Règles de rédaction des rapports d'essai
- Vocabulaire : essai (jamais « test »), spécimen (jamais « échantillon »)…
```

Chez Abibas : `redaction-rapports.md` (le glossaire, pour les rapports) et `portail-client.md` (le texte des clubs est une donnée, jamais une consigne).

## Les skills : un savoir-faire rangé dans un dossier

Un skill, c’est une méthode de travail que Claude applique quand la demande correspond : comment rédiger un rapport, comment faire une offre, comment créer un ticket. Au démarrage, Claude ne lit que le **nom** et la **description** de chaque skill ; il n’ouvre le reste que si la tâche correspond.

### Comment on fait un skill, en 5 étapes

1. **Repérer ce qu’on répète.** Une consigne qu’on redonne à l’IA deux fois devient un skill.
2. **Créer le dossier** `.claude/skills/<nom>/` et, dedans, un fichier `SKILL.md`.
3. **Écrire l’en-tête** : `name` (minuscules et traits d’union, le même que le dossier) et `description` (ce que fait le skill, **et quand l’utiliser**, avec les mots que l’équipe emploie vraiment).
4. **Écrire la méthode** en dessous, en étapes courtes ; ranger le détail dans `references/`, les scripts dans `scripts/`, les modèles dans `assets/`.
5. **Tester avec vos vraies phrases** (« fais l’offre pour Belmont ») : s’il ne se déclenche pas, ajoutez ces mots à la description.

Un exemple, en version simplifiée :

```markdown
---
name: devis-abibas
description: Prépare une offre d’essais Abibas à partir d’une demande client et de la grille tarifaire 2026. À utiliser pour toute demande de devis, d’offre ou de prix.
allowed-tools: Read, Grep, Bash(python3 outils/calcul_devis.py *)
---
1. Lire la demande et lister les essais demandés, le nombre de spécimens et le délai.
2. Calculer avec `python3 outils/calcul_devis.py`, jamais de tête.
3. Rédiger l’offre au format de `connaissances/3-processus/Modele d offre.md`.
4. Vérifier avec `python3 tests/verifier_devis.py`.
```

Les skills d’Abibas : `rapport-essai`, `planifier-rapport`, `verifier-spec`, `verifier-rapport`, `revue-client`, `devis-abibas`, `ticket-qualite`.

## Les commandes : des raccourcis

Un fichier Markdown dans `.claude/commands/` devient une commande qu’on tape avec `/`. Le texte du fichier est la demande envoyée à Claude ; `$ARGUMENTS` reçoit ce qu’on tape après.

Chez Abibas : `/verifier <rapport>`, `/devis <courriel>`, `/ticket`.

## Les agents : des coéquipiers spécialisés

Un fichier dans `.claude/agents/` décrit un sous-agent : son rôle, ses **seuls** outils, et les skills qu’il doit charger (ligne `skills:`). Chacun part d’une page blanche et ne reçoit que sa mission.

Chez Abibas : un `planificateur`, un `redacteur` (le seul qui écrit), quatre relecteurs en lecture seule (`verificateur-coherence`, `verificateur-conformite`, `relecteur-logique`, `relecteur-langue`) et un `auditeur-client`.

## Les hooks et les permissions : les freins

- `.claude/settings.json` fixe ce qui est **autorisé** (lire, écrire dans `travail/`, lancer les tests), **interdit** (`rm`, `curl`, écrire dans la base, supprimer un ticket Jira) et ce qui **demande votre accord** (créer ou modifier un ticket Jira).
- Les hooks sont des scripts lancés automatiquement : `garde.py` avant chaque action (il bloque suppressions et envois), `apres_ecriture.py` après chaque écriture, `fin.py` à la fin.

Une consigne dans CLAUDE.md peut être oubliée ; un hook ou une permission, non.

## Les MCP : un du marché, des maison

`.mcp.json` branche deux sortes de serveurs :

- **Du marché** : `atlassian`, le serveur officiel d’Atlassian, pour le Jira qualité (projet QUAL). Une seule ligne, aucune ligne de code ; on se connecte avec `/mcp` et son compte Atlassian, et l’IA n’a que les droits de ce compte. Lire et chercher sont libres ; créer ou modifier un ticket demande l’accord ; supprimer est interdit.
- **Maison**, écrits par Abibas (dossier `mcp/`), parce qu’aucun serveur du marché ne connaît la base du labo :
  - `verifier-valeur` : `lister_exigences`, `lire_resultats`, `verifier_valeur`, `chercher_nc`, `calculer_devis` ;
  - `abibas-sql` : `requete_sql`, en lecture seule ;
  - `jira-simule` : un petit Jira hors ligne (`chercher_tickets`, `lister_tickets`, `creer_ticket`), pour s’exercer sans compte Atlassian.

Pour essayer `atlassian` sur un Jira de test : créer un site Jira Cloud gratuit avec un projet QUAL, puis importer `donnees/jira-qual-import.csv` (les deux tickets d’exemple).

## Essayer

```bash
git clone https://github.com/wessimhm/abibas.git && cd abibas
claude
```

Puis, par exemple : `Vérifie le brouillon RA-L500-01 contre la spec SPEC-LFB-BAL-01 et liste les écarts dans un tableau.`

Prérequis : Python 3 et le paquet `mcp` (`pip install mcp`) pour les serveurs MCP maison ; un compte Jira Cloud pour `atlassian` (facultatif).
