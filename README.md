# Socle commun Memnius

Règles et garde-fous communs à tous les dépôts de sujet du groupe d'étude Memnius.

| Fichier | Contenu |
|---|---|
| [`REGLES.md`](REGLES.md) | texte de référence : C1–C10, A1–A6, R1–R8, O1–O8, journal, passation |
| [`regles.yaml`](regles.yaml) | liste des règles et gardes, lue par la garde A5 |
| [`gardes/gardes.py`](gardes/gardes.py) | gardes A2 à A6 (CI et pre-commit) |
| [`tests/`](tests/) | chaque garde testée dans les deux sens |
| [`decisions/`](decisions/) | journal des décisions du socle |
| `.github/workflows/gardes.yml` | workflow réutilisable appelé par chaque sujet |
| `.pre-commit-hooks.yaml` | crochet local facultatif (A2 et A6) |

Version publiée : étiquette `v1`. Les sujets l'appellent par le workflow réutilisable `.github/workflows/gardes.yml@v1`.
Le comité du socle (pour l'instant Romain seul, décision 0004) valide toute pull request.
