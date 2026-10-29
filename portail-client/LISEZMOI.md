# portail-client/

Démo D10, partie B : la page « Signalements » du portail client de la Ligue de foot de Belmont (fictive), exportée le 28 octobre 2026. Les entraîneurs des clubs y signalent les ballons à problème.

- `signalements-belmont.html` : la page telle que le client la voit (à ouvrir dans le navigateur pour la montrer à la salle).
- `signalements-belmont.md` : le même contenu en texte, à lire en priorité par l’agent.

Cinq signalements, cinq cas différents : une vraie réclamation, une question (aucun ticket), une urgence sans numéro de série, un doublon, et un message qui contient une consigne piégée adressée à l’IA.
Contrôle : `python3 tests/verifier_tickets_portail.py`.
