# TD2 Next Generation AI — Groupe B

**Version indépendante, consacrée au diagnostic SQL d'un accord erroné.**
ESILV, séance du 18 novembre 2026, énoncé `2026-11-18-students-5`.

Le cas réel **C02** contient deux réponses identiques mais fausses : GPT-OSS 20B et Dots
retournent **0**, contre **590 320 centimes HT (5 903,20 €)**. Les deux requêtes sont
reproduites sur la base officielle. Le diagnostic retrouve **6 clients et 82 lignes de
commande** qui expliquent la totalité de l'écart. Un calcul Python indépendant sur les
CSV donne les mêmes clients et montants.

**Le panel officiel 2/3 répond correctement ; le quorum 3/5 s'abstient.**
Il serait faux d'affirmer que le zéro gagne l'un de ces deux votes.
Un panel illustratif différent, explicitement choisi après observation des traces,
montre aussi comment ce zéro peut obtenir 2 voix sur 3.

## Lire les livrables

- [Rapport demandé : reports/td2.md](reports/td2.md) : cas, décompte manuel, deux SQL complets,
  diagnostic, requête delta, résultats, limites et contributions.
- [Preuve par client](evidence/delta-c02.csv) et [82 lignes de commande](evidence/independent-csv-order-lines.csv).
- [Résultats vérifiés](evidence/summary.json), [96 requêtes rejouées](evidence/sql-replay.csv)
  et [journal des tests](evidence/tests.txt).
- [Traces TD1 intactes](traces-td1.csv), [références TD1 intactes](reference-td1.csv)
  et [provenance avec empreintes](sources/provenance.json).
- [Prompts retrouvés](prompts/README.md) et [guide pour expliquer le travail](reports/explication-orale.md).
- [Annexe de contrôle des votes sur 20 questions](reports/annexe-votes.md).

## Reproduire

Python **3.11 ou plus récent** avec SQLite (bibliothèque standard). Aucun paquet à installer,
aucune clé, aucun appel aux modèles, aucun accès réseau nécessaire après récupération du dépôt.
Dans le dossier du dépôt :

```sh
python reproduce.py
```

Sur un système où l'exécutable s'appelle `python3`, utiliser `python3 reproduce.py`.
Cette commande exécute les tests, vérifie les empreintes, rejoue le SQL en lecture seule,
recrée les preuves, puis contrôle C02 avec l'atelier officiel. Elle doit terminer avec
« Toutes les vérifications ont réussi ». Les fichiers sous `evidence/` sont réécrits ;
les traces et les données sources restent intactes.

Commandes séparées :

```sh
python -m unittest discover -s tests -v
python analyse.py
python atelier-vote.py
python atelier-vote.py --traces traces-td1.csv --case C02
```

Les quatre exemples de la première commande `atelier-vote.py` sont **synthétiques**.
Ils ne sont pas des sorties réelles de modèles. `analyse.py` et le second appel à
l'atelier utilisent uniquement les traces TD1 conservées. Les requêtes manuelles sont
dans [sql/](sql/) ; elles peuvent aussi être exécutées dans un lecteur SQLite.

## Code à comprendre

1. `analyse.py` sélectionne la dernière tentative par cellule et cherche les erreurs partagées.
2. `Orchestrateur.vote_k_sur_n` dans `skeleton-multi-llm-en.py` compte les valeurs sans consulter
   la référence. C'est la seule méthode modifiée du squelette officiel.
3. `sql/delta-c02.sql` compare, pour chaque ligne de commande, les trois conditions de sélection.
4. `independent_csv()` recalcule les âges et les revenus avec des dates et dictionnaires Python.

Le squelette et le contrôle SQLite proviennent du cours. Le code d'analyse, le diagnostic,
les tests et les rapports TD2 ont été réalisés pour cette version, sans consulter le dépôt
TD2 produit par le groupe avec Claude. L'accès aux traces et au script du TD1 est réutilisé.

## Périmètre et remise

Ce dépôt livre **la partie B**. La fonction de vote et l'annexe servent à vérifier ses conclusions.
Il ne prétend pas livrer la règle de routage ni le simulateur du groupe C. Il ne remplace pas
à lui seul la remise complète A/B/C du sous-groupe.

L'énoncé prévoit un dépôt commun TD1–TD3, une relecture croisée et une remise Moodle.
Ce dépôt séparé répond à la demande d'un travail indépendant. L'intégration éventuelle au dépôt
commun, les noms et contributions humaines, la relecture en groupe et la remise Moodle restent
à effectuer. Aucun résultat de quiz, échange en plénière ou validation humaine n'est inventé.

Échéance indiquée dans l'énoncé : **dimanche 22 novembre 2026 à 23 h 59, heure de Paris**.
Voir [REMISE.md](REMISE.md) pour les éléments de publication et les liens à remettre.

Sources : [énoncé officiel](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/kit-td1/enonce-td2-en.html)
et [références officielles](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/reference-values-td1-en.html).
Les copies des sources et leurs empreintes figent la version effectivement utilisée.
