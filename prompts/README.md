# Prompts et assistance

Le script TD1 local `esilv-student-2026-10-18/kit-td1/skeleton-multi-llm-en.py` a été retrouvé.
Sa copie est [sources/skeleton-td1-original.py](../sources/skeleton-td1-original.py).
Elle est identique octet pour octet au squelette officiel téléchargé le 18 novembre 2026.

Les littéraux `SYSTEM_PROMPT` et `USER_PROMPT_TEMPLATE` ont été extraits de ce fichier,
puis développés avec le schéma TD1 local et les questions exactes des traces.
Ils sont conservés dans `system.txt`, `user-template.txt`, `schema-td1.sql` et les vingt
fichiers `C01-user.txt` à `C20-user.txt`.

Pour chacune des vingt questions, le SHA-256 de `system + "\n" + user` correspond à celui
de toutes ses lignes dans les 106 traces. Voir [la vérification](../evidence/prompt-checks.csv).
Ce contrôle atteste les textes retrouvés ; il ne constitue pas un nouvel appel réseau.

**TD2 : aucun prompt de génération SQL modifié et aucune nouvelle inférence demandée.**
Le travail consiste à analyser des sorties conservées et à écrire du SQL de diagnostic.
Les fichiers d'état complets et la configuration historique de chaque poste n'ont pas été
assemblés : ils ne sont pas nécessaires à cette reproduction hors ligne.

Le prompt d'assistance effectivement reçu pour cette version est conservé dans
[demande-td2.txt](demande-td2.txt). Codex a écrit le code d'analyse, les tests, le diagnostic
et la rédaction. Les consignes internes de l'outil ne sont pas des prompts expérimentaux TD1.
La compréhension et la validation humaine restent à réaliser avant une remise sous le nom des membres.
