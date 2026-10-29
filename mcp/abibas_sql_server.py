#!/usr/bin/env python3
"""
Serveur MCP « SQL générique » d’Abibas : « abibas-sql ». Démo formation IA, vendredi 2 (fictif).

Un seul outil : requete_sql(requete). Le modèle écrit lui-même le SQL.
Puissant et souple, mais il voit toute la base et peut se tromper de requête.
Garde-fous : base ouverte en lecture seule (mode=ro), une seule instruction SELECT ou WITH,
200 lignes au maximum, chaque appel journalisé dans donnees/journal-mcp.log.

Lancement : python3 mcp/abibas_sql_server.py   (Claude le lance tout seul via .mcp.json)
Essai sans Claude : python3 mcp/abibas_sql_server.py --test
Dépendance : pip install mcp. Sans le SDK, requete_sql reste importable et testable.
"""
import datetime
import json
import os
import re
import sqlite3
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RACINE, "donnees", "abibas-labo.db")
JOURNAL = os.path.join(RACINE, "donnees", "journal-mcp.log")
MAX_LIGNES = 200
INTERDITS = r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|PRAGMA|VACUUM|REINDEX|TRUNCATE|GRANT|BEGIN|COMMIT|ROLLBACK|SAVEPOINT|RELEASE|LOAD_EXTENSION)\b"


def _journal(arguments, resultat):
    try:
        court = " ".join(str(resultat).split())[:140]
        with open(JOURNAL, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} | abibas-sql | requete_sql | "
                    f"{json.dumps(arguments, ensure_ascii=False)} | {court}\n")
    except Exception:
        pass


def _val(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return (str(int(v)) if v.is_integer() else str(v)).replace(".", ",")
    return str(v)


def requete_sql(requete: str) -> str:
    """Exécute UNE requête SQL en lecture seule sur la base du labo Abibas (SQLite) et rend le résultat.

    requete : une seule instruction SELECT (ou WITH … SELECT). Toute écriture ou commande
    (INSERT, UPDATE, DELETE, DROP, ALTER, ATTACH, PRAGMA…) est refusée. 200 lignes au maximum.
    Tables disponibles :
      exigences(id, essai, parametre, operateur, valeur_critere, unite, revision)
      resultats(id, exigence, parametre, valeur, unite, sn, remarque)
      non_conformites(id, produit, essai, description, cause, action, statut, date_cloture)
      tarifs(essai, prix, delai_jours)
    Attention : resultats.valeur est parfois un texte (« 1 h 30 / 1,8 », « — ») ; vérifier l'unité de chaque ligne.
    Ne prononce aucune conformité : c'est le rôle de l'ingénieure responsable.
    """
    args = {"requete": requete}
    q = (requete or "").strip().rstrip(";").strip()
    sans_chaines = re.sub(r"'[^']*'", "''", q)
    if not re.match(r"^(SELECT|WITH)\b", sans_chaines, re.I):
        _journal(args, "REFUSÉE : pas un SELECT")
        return "REFUSÉE : seules les requêtes SELECT (ou WITH … SELECT) sont permises. La base est en lecture seule."
    if ";" in sans_chaines:
        _journal(args, "REFUSÉE : plusieurs instructions")
        return "REFUSÉE : une seule instruction à la fois."
    m = re.search(INTERDITS, sans_chaines, re.I)
    if m:
        _journal(args, f"REFUSÉE : {m.group(1).upper()}")
        return f"REFUSÉE : le mot-clé {m.group(1).upper()} est interdit. Lecture seule, SELECT uniquement."
    if not os.path.exists(BASE):
        return f"ERREUR : base introuvable : {BASE} (lancer python3 outils/creer_base.py)"
    try:
        cx = sqlite3.connect(f"file:{BASE}?mode=ro", uri=True)
        cur = cx.execute(q)
        noms = [c[0] for c in cur.description] if cur.description else []
        rangs = cur.fetchmany(MAX_LIGNES + 1)
        cx.close()
    except sqlite3.Error as e:
        _journal(args, f"ERREUR SQL : {e}")
        return f"ERREUR SQL : {e}"
    tronque = len(rangs) > MAX_LIGNES
    rangs = rangs[:MAX_LIGNES]
    lignes = [" | ".join(noms), " | ".join("---" for _ in noms)]
    lignes += [" | ".join(_val(v) for v in r) for r in rangs]
    lignes.append(f"({len(rangs)} ligne(s){', tronqué à 200' if tronque else ''})")
    _journal(args, f"{len(rangs)} ligne(s)")
    return "\n".join(lignes)


def _test():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for q in ["SELECT id, valeur FROM resultats WHERE exigence='EX-02'",
              "SELECT id, valeur, unite FROM resultats WHERE unite = '°F'",
              "DELETE FROM resultats",
              "SELECT 1; DROP TABLE resultats",
              "PRAGMA table_info(resultats)"]:
        print(f"requete_sql({q!r}) ->\n{requete_sql(q)}\n")


def _serveur():
    try:  # SDK MCP 2.x
        from mcp.server.mcpserver import MCPServer as Serveur
    except ImportError:
        try:  # SDK MCP 1.x
            from mcp.server.fastmcp import FastMCP as Serveur
        except ImportError:
            print("ERREUR : SDK MCP absent. Installez-le : pip install mcp.", file=sys.stderr)
            sys.exit(3)
    serveur = Serveur("abibas-sql")
    serveur.tool()(requete_sql)
    return serveur


if __name__ == "__main__":
    if "--test" in sys.argv:
        _test()
    else:
        _serveur().run()
