# Consignes pour les agents IA : dépôt du socle

Ce dépôt contient les règles communes à tous les sujets Memnius (`REGLES.md`), leur liste
(`regles.yaml`), les gardes automatiques (`gardes/gardes.py`) et leurs tests (`tests/`).

- Les règles appartiennent au comité du socle (C3). Tu peux proposer, par une pull request
  sur une branche `agent/<outil>/<objet>` ; tu ne fusionnes jamais toi-même.
- Toute modification d'une règle ou d'une garde commence par une nouvelle entrée de `decisions/` (C2).
- Une règle retirée n'est jamais supprimée de `regles.yaml` : elle passe à `abrogee: true`.
- Toute garde modifiée garde ses deux tests (cas sain accepté, cas fautif refusé) et `python3 -m unittest discover -s tests` reste vert.
- Commits terminés par `Assisted-by: <outil> (<modèle>)` (C4) ; réponse dans la langue de ton interlocuteur (C10).
- En fin de session, mets `PASSATION.md` à jour (C9).
