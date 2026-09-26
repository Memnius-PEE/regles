# Passation — 2026-09-26 — rédigée par un agent (Claude), vérifiée par : —

## 0. En une phrase *
Socle v1 prêt à publier : règles, gardes A2 à A6 et leurs tests ; aucune étiquette v1 posée tant que le dépôt n'est pas sur GitHub.

## 1. État mesuré *
Tests des gardes lancés hors GitHub, dans le kit préparé le 2026-09-26 (voir LISEZMOI.md du kit) ;
à re-mesurer après la première publication avec `python3 -m unittest discover -s tests -v`.

## 3. Décisions prises (numéros du journal)
0001 à 0010 : décisions du 2026-09-26 (0010 remplace 0002 : GitHub au lieu de GitLab.com).

## 5. Ce qui reste dû ou en cours *
1. Publier ce dépôt dans l'organisation GitHub (dépôt regles) et poser l'étiquette v1.
2. Ajouter un ou deux membres au comité du socle (0004).
3. Construire l'archiviste (réservé par 0009, conception en attente).

## 7. Ce qui n'a PAS été vérifié *
- Les workflows GitHub Actions (gardes, gitleaks, tests) n'ont pas tourné sur GitHub.
- La garde A5 ne vérifie que les renvois nommés (C3, R5…), pas les phrases qui comptent les règles.
