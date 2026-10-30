---
description: Remet le dépôt comme au premier jour, avant les démos (réservé au formateur)
disable-model-invocation: true
allowed-tools: Bash(python3 outils/reinitialiser_demo.py), Bash(python3 outils/reinitialiser_demo.py --oui)
---

Le formateur lance lui-même cette commande : c'est sa décision explicite de remettre à zéro les fichiers produits par les démos (règle 5 : un humain décide d'une suppression ; ici, c'est lui).

1. Lance `python3 outils/reinitialiser_demo.py` et montre la liste de ce qui sera remis à zéro.
2. Lance `python3 outils/reinitialiser_demo.py --oui`.
3. Termine par une ligne : combien de fichiers remis d'origine, combien supprimés, et le rappel de ce qui est hors du dépôt (affiché par le script). Puis conseille `/clear` pour repartir avec une conversation vide.

N'utilise aucune autre commande de suppression.
