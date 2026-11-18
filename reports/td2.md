# TD2 — Groupe B : un accord erroné réel sur C02

ESILV · Next Generation AI · 18 novembre 2026  
Version indépendante du dépôt TD2 du groupe avec Claude.  
Source : [énoncé officiel, étape 2](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/kit-td1/enonce-td2-en.html#section-7), pack `2026-11-18-students-5`.

## 1. Résultat et périmètre

**C02 présente une valeur erronée partagée : GPT-OSS 20B et Dots retournent tous deux 0,
au lieu de 590 320 centimes HT.** La reproduction SQL et une vérification indépendante
sur les CSV confirment l'erreur. Six clients et 82 lignes de commande expliquent tout l'écart.

Le zéro ne gagne **ni** le panel officiel 2/3 **ni** le quorum 3/5 : le premier obtient la
bonne valeur et le second s'abstient. Nous distinguons donc l'accord erroné entre deux modèles
d'une majorité erronée dans un panel donné. Le cas répond à la définition de l'étape B,
qui demande au moins deux modèles partageant la même mauvaise valeur, même s'ils sont
mis en minorité. **Le cas de secours DEMO-SQL-C11 n'est pas utilisé.**

Ce rapport couvre B. La fonction de vote et l'annexe servent de contrôle indépendant des
décomptes. La règle de routage, le simulateur C et les contributions A/C du groupe ne sont
pas présentés comme accomplis ici. Aucun dépôt ni livrable TD2 produit avec Claude n'a été consulté.

## 2. Données, sélection et traçabilité

Les fichiers TD1 `traces-td1.csv` et `reference-td1.csv` ont été retrouvés dans les
téléchargements. Les traces sont identiques à celles de l'archive `DIA1-G2_TD1.zip`.
Le kit TD1 local fournit aussi le script d'origine et le schéma utilisés pour les prompts.
La base téléchargée depuis le site officiel est identique à la base du kit local :

```text
SHA-256 boutique.sqlite
0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2
```

La provenance et les empreintes des entrées sont conservées dans
[sources/provenance.json](../sources/provenance.json). La base et les CSV sont inclus pour
permettre une reproduction sans réseau. Les valeurs sont des entiers en centimes HT.

- 106 enregistrements TD1, tous marqués `nature=real`, dont six reprises.
- 100 cellules finales : vingt questions × cinq couples fournisseur/modèle.
- Sélection : dernière ligne de chaque cellule, comme l'atelier officiel. Le programme
  vérifie que les tentatives de chaque cellule sont chronologiques et partagent le même prompt.
  Un test vérifie aussi que le classement du TD1 `(attempts, date_utc, ordre)` donne les mêmes lignes.
- Les 100 cellules finales contiennent 78 valeurs correctes, 18 incorrectes, un SQL invalide,
  une sortie SQL rejetée et deux indisponibilités. Aucune reprise ne crée une voix supplémentaire.
- La recherche couvre les cinq modèles : **C02 est l'unique question avec une valeur fausse
  partagée** dans les cellules finales. Voir [le résultat de recherche](../evidence/shared-wrong-values.json).

Ces traces attestent des résultats conservés du TD1, pas de nouveaux appels. Ce TD2 ne
contacte aucun fournisseur. Les réexécutions SQL sont explicitement des `sql_replay` dans
[le journal de reproduction](../evidence/sql-replay.csv) et ne modifient pas les traces originales.

## 3. Identification du cas et votes

**Question C02 :** chiffre d'affaires total HT, en centimes, de toutes les commandes des
clients ayant exactement 25 ans au **25 septembre 2026**. La date détermine l'âge du client,
elle ne restreint pas la date de ses commandes.

La référence TD1 vaut **590 320 centimes = 5 903,20 €**. Sa requête a été rejouée et elle
concorde aussi avec le [corrigé officiel publié](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/reference-values-td1-en.html).
Le contrôle Python sur les CSV constitue la vérification indépendante détaillée ci-dessous.

| Fournisseur / modèle demandé | Valeur | Verdict TD1 | Enregistrement CSV |
|---|---:|---|---:|
| groq / `openai/gpt-oss-120b` | 590320 | correct | 2 |
| groq / `openai/gpt-oss-20b` | 0 | incorrect | 22 |
| openrouter / `cohere/north-mini-code:free` | 2606320 | incorrect | 44 |
| groq / `qwen/qwen3.8-27b` | 590320 | correct | 64 |
| openrouter / `dots-studio/dots-3-note-preview:free` | 0 | incorrect | 91 |

Les numéros désignent des **enregistrements CSV à partir de 1, hors en-tête**, pas les
lignes physiques du fichier : les requêtes SQL occupent plusieurs lignes. Les cinq appels
C02 ont un statut HTTP 200. Voir [les cinq traces complètes](../evidence/c02-traces.csv).

### Décompte manuel puis vérification par code

| Panel déclaré | Valeurs comptées | Seuil | Résultat |
|---|---|---|---|
| Fixe officiel : GPT-OSS 120B, Cohere, Qwen | 590320 : 2 voix ; 2606320 : 1 voix | 2 sur 3 | Consensus 590320, correct |
| Les cinq modèles TD1 | 590320 : 2 voix ; 0 : 2 voix ; 2606320 : 1 voix | 3 sur 5 | Abstention ; maximum 2 voix |

**GPT-OSS 20B et Dots ne font pas partie du panel fixe officiel.** Ils ne doivent pas être
substitués à 120B ou Qwen pour faire artificiellement gagner zéro dans ce panel.
Le vote reçoit seulement les valeurs et l'état d'exécution ; la référence et les verdicts
« correct/incorrect » ne sont pas transmis au vote. Le contrôle vient après la décision.

La fonction `vote_k_sur_n` est implémentée dans le squelette du cours ; son contrat interdit
les doublons fournisseur/modèle, impose une majorité stricte et conserve les indisponibles
dans n. La sortie `votes=2` en abstention est le plus grand nombre de voix pour une valeur,
pas une valeur retenue. La valeur finale reste `None` et la liste des modèles gagnants reste vide.

Les décomptes sont vérifiés par [quorums.json](../evidence/quorums.json) et par l'atelier
officiel sur C02, [sortie conservée](../evidence/official-c02-vote.txt).
La méthode du binôme A du groupe n'était pas fournie : nous n'affirmons donc pas avoir
effectué sa relecture croisée. La vérification utilise ici notre implémentation indépendante
du contrat officiel. L'[annexe](annexe-votes.md) permet une comparaison sur les vingt questions.

### Illustration complémentaire, choisie après observation

Si l'on constitue le panel **GPT-OSS 20B / Dots / Cohere**, avec k=2 et n=3, les valeurs réelles
conservées `[0, 0, 2606320]` donnent un **consensus erroné 0 à 2/3**. C'est un calcul post hoc
sur les mêmes traces, sans nouvelle inférence. Ce panel n'est pas celui prescrit pour la
comparaison officielle ; il ne constitue ni une politique évaluée à l'avance ni une mesure
généralisable de fiabilité. Voir [le résultat étiqueté](../evidence/c02-posthoc-panel.json).

## 4. Deux requêtes fautives et cause exacte

Les fichiers ci-dessous reprennent les requêtes intégrales des traces, sans correction.
Le programme vérifie cette identité avant d'exécuter l'analyse.

### M1 — GPT-OSS 20B, Groq

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price),0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date > '2025-09-25' AND c.birth_date <= '2026-09-25';
```

**Résultat exécuté : 0.** La condition sélectionne les naissances dans
`]2025-09-25 ; 2026-09-25]`, donc des personnes de moins d'un an à la date de référence.
Elle ne sélectionne pas les personnes de 25 ans. Aucun client de cette base n'appartient
à cette fenêtre. Les jointures et la multiplication quantité × prix sont cohérentes ;
c'est le filtre de naissance qui est incorrect.

### M2 — Dots, OpenRouter

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (
    CAST(substr(c.birth_date, 1, 4) AS INTEGER) + 25 = 2026
    AND substr(c.birth_date, 6, 2) = '09'
    AND substr(c.birth_date, 9, 2) = '25'
)
AND o.date >= '2026-09-25 00:00:00'
AND o.date < '2026-09-26 00:00:00';
```

**Résultat exécuté : 0.** Les trois premières conditions imposent exactement la naissance
le **25 septembre 2001** : elles sélectionnent le jour du 25e anniversaire, pas toute
l'année où l'âge révolu vaut 25. Seul C001 satisfait cette condition de naissance.

Un second défaut impose en plus une commande dans `[2026-09-25 ; 2026-09-26[`, ce que
la question ne demande pas. La dernière commande de la base est le **20 septembre 2026
à 19:24:25**. Aucune commande ne peut satisfaire ce filtre, même pour C001.

Ces mécanismes sont séparés dans [diagnostic-m2.sql](../sql/diagnostic-m2.sql) :

| Variante de diagnostic, écrite pour l'analyse | Montant exécuté |
|---|---:|
| Garder la naissance le 25/09/2001, retirer le filtre des commandes | 135000 |
| Corriger la fenêtre d'âge, conserver le mauvais filtre des commandes | 0 |
| Corriger la fenêtre d'âge et prendre toutes les commandes | 590320 |

Ces variantes sont des diagnostics rédigés pendant TD2, **pas des réponses de modèles**.
Les deux modèles produisent donc le même zéro par des conditions différentes. Le résultat
vide est transformé en zéro par `COALESCE(SUM(...), 0)`. Un SQL exécutable et un résultat
du bon type ne suffisent pas à démontrer le respect de la question.

### Référence correcte

Avoir 25 ans révolus le 25/09/2026 impose `2000-09-25 < birth_date <= 2001-09-25`.
La borne de 2000 est exclue car ces clients ont déjà 26 ans. Celle de 2001 est incluse
car ils viennent d'avoir 25 ans. Les dates ISO fixes se comparent chronologiquement en texte.
Il n'y a aucun filtre sur les dates de commande :

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p ON p.product_id = o.product_id JOIN customers AS c ON c.customer_id = o.customer_id WHERE c.birth_date > '2000-09-25' AND c.birth_date <= '2001-09-25';
```

**Résultat exécuté : 590320.** Pour corriger M1, remplacer sa fenêtre de naissance.
Pour corriger M2, remplacer ses conditions de naissance par cette même fenêtre et supprimer
les deux conditions sur `o.date`. Les jointures restent les mêmes.

## 5. Diagnostic delta exécuté sur boutique.sqlite

La requête suivante construit, pour chaque ligne de commande, trois indicateurs reprenant
exactement les conditions de la référence, de M1 et de M2. Elle calcule les montants comptés
et les différences signées **référence − modèle** pour chaque client. Un montant positif
est omis par le modèle ; un montant négatif serait ajouté à tort. Le `HAVING` retient les
clients dont au moins une ligne diffère. La clé d'une ligne de commande est
`(order_id, product_id)` : on n'élimine pas les paniers à plusieurs produits.

```sql
-- Une ligne de commande = (order_id, product_id), pas seulement order_id.
-- Chaque indicateur reprend exactement le WHERE de la requête concernée.
WITH lignes AS (
    SELECT c.customer_id, c.birth_date, o.order_id, o.product_id,
           o.quantity_product * p.price AS amount_cents,
           CASE WHEN c.birth_date > '2000-09-25'
                 AND c.birth_date <= '2001-09-25' THEN 1 ELSE 0 END AS ref,
           CASE WHEN c.birth_date > '2025-09-25'
                 AND c.birth_date <= '2026-09-25' THEN 1 ELSE 0 END AS m1,
           CASE WHEN CAST(substr(c.birth_date, 1, 4) AS INTEGER) + 25 = 2026
                 AND substr(c.birth_date, 6, 2) = '09'
                 AND substr(c.birth_date, 9, 2) = '25'
                 AND o.date >= '2026-09-25 00:00:00'
                 AND o.date < '2026-09-26 00:00:00' THEN 1 ELSE 0 END AS m2
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN product p ON p.product_id = o.product_id
)
SELECT customer_id, birth_date,
       SUM(ref) AS reference_order_lines,
       SUM(amount_cents * ref) AS reference_cents,
       SUM(amount_cents * m1) AS m1_cents,
       SUM(amount_cents * m2) AS m2_cents,
       SUM(amount_cents * (ref - m1)) AS delta_m1_cents,
       SUM(amount_cents * (ref - m2)) AS delta_m2_cents
FROM lignes
GROUP BY customer_id, birth_date
HAVING SUM(CASE WHEN ref != m1 OR ref != m2 THEN 1 ELSE 0 END) > 0
ORDER BY customer_id;
```

### Résultat obtenu

| Client | Naissance | Lignes de commande | Référence HT, centimes | M1 | M2 | Delta M1 | Delta M2 |
|---|---|---:|---:|---:|---:|---:|---:|
| C001 | 2001-09-25 | 18 | 135000 | 0 | 0 | 135000 | 135000 |
| C002 | 2001-09-24 | 6 | 25920 | 0 | 0 | 25920 | 25920 |
| C005 | 2000-09-26 | 20 | 150240 | 0 | 0 | 150240 | 150240 |
| C007 | 2000-11-30 | 18 | 118740 | 0 | 0 | 118740 | 118740 |
| C008 | 2001-05-15 | 11 | 99090 | 0 | 0 | 99090 | 99090 |
| C009 | 2001-03-10 | 9 | 61330 | 0 | 0 | 61330 | 61330 |
| **Total** | | **82** | **590320** | **0** | **0** | **590320** | **590320** |

`135000 + 25920 + 150240 + 118740 + 99090 + 61330 = 590320`.

Pour chacune des deux requêtes, **590320 − 0 = 590320 centimes** : le delta explique la
totalité de l'erreur. Il n'y a aucune ligne ajoutée à tort sur cette base. Les clients sans
commande ne contribuent pas à l'écart de revenu et ne figurent pas dans ce résultat.

Fichiers : [delta SQL par client](../evidence/delta-c02.csv),
[calcul CSV indépendant par client](../evidence/independent-csv-customers.csv) et
[les 82 lignes de commande](../evidence/independent-csv-order-lines.csv).

## 6. Contrôle indépendant et tests

Le contrôle `independent_csv()` lit directement `customers.csv`, `orders.csv` et `product.csv`,
sans SQL ni interrogation de SQLite. Il calcule l'âge avec :

```python
age = date_reference.year - naissance.year
age -= (date_reference.month, date_reference.day) < (naissance.month, naissance.day)
```

Il retient l'âge égal à 25, associe chaque commande à son client et au prix du produit,
puis additionne `quantity_product * price` en entiers. Les six clients et les montants par
client concordent avec le diagnostic SQL. Cette méthode vérifie la logique de sélection
avec une autre implémentation, mais réutilise les mêmes données officielles : elle ne prouve
pas que ces données représentent une activité commerciale réelle.

Exécution locale : Python 3.14.3, SQLite 3.52.0, Windows. La base a été produite avec SQLite
3.45.1 selon son manifeste ; son empreinte est inchangée. Le projet demande Python 3.11+.

**Vérifications réalisées :**

- 11 tests automatisés passent : quatre exemples officiels, seuils invalides, doublons,
  erreurs/indisponibilités, valeur zéro, listes des gagnants, sélection des tentatives,
  cas réel C02, bornes d'âge, delta SQL/CSV et contre-exemple d'ajout erroné.
- Les 96 requêtes TD1 portant `correct` ou `incorrect` reproduisent toutes leur valeur stockée.
- Les 20 requêtes de référence reproduisent leurs valeurs, toutes identiques au corrigé officiel.
- Les 20 prompts reconstruits depuis le script retrouvé correspondent aux empreintes
  de toutes les traces de leur question.
- Les deux SQL fautifs donnent 0 ; la référence et le contrôle CSV donnent 590320.
- Les sources et la base gardent leurs empreintes avant et après l'exécution.

Les tests avec dates de naissance construites et base en mémoire sont explicitement
synthétiques ; ils n'entrent pas dans l'analyse des 100 cellules. Les erreurs API et les
sorties SQL invalides/rejetées restent dans les traces ; elles ne sont pas présentées comme
des montants réexécutés. Voir [tests.txt](../evidence/tests.txt),
[summary.json](../evidence/summary.json), [sql-replay.csv](../evidence/sql-replay.csv) et
[reference-checks.csv](../evidence/reference-checks.csv).

Reproduction depuis la racine :

```sh
python reproduce.py
```

La commande échoue si un test, une empreinte ou une égalité attendue ne tient pas.
Le contrôle SQLite du cours ouvre la base en lecture seule, limite les requêtes et refuse
les écritures. Aucun service externe ni clé API n'est requis.

## 7. Conséquence pour le contrôle et limites

L'accord sur un chiffre ne valide pas la sémantique d'une condition d'âge. Des familles
de modèles distinctes peuvent échouer différemment et arriver au même zéro. Sur C02,
passer à cinq modèles enlève un consensus correct et conduit à une abstention ; sur C19,
ce même changement crée un consensus correct. Plus de modèles ne signifie donc pas
automatiquement une meilleure disponibilité, ni une garantie universelle d'exactitude.

Pour un chiffre affiché au client ou un paiement, ce cas motive une vérification
déterministe de la fenêtre d'âge, des lignes retenues et du montant, ou une revue si le
quorum s'abstient. Ce constat est une conséquence du diagnostic B, pas une règle de
routage complète prétendument validée pour le groupe C.

Limites : un lot, une base, vingt questions ; aucune mesure de corrélation statistique
entre erreurs, aucune garantie future. Le vote sur un panel illustratif choisi a posteriori
ne doit pas servir à estimer un taux de risque. L'exécution sur une seconde machine et
la relecture croisée humaine ne sont pas attestées par ces tests locaux.

## 8. Contributions, état de remise et prochaines étapes

| Intervenant / partie | Contribution attestée dans cette version |
|---|---|
| Demandeur | Demande d'une réalisation indépendante, limitée à B, avec publication GitHub si possible |
| Assistance Codex | Recherche des entrées TD1, code B, adaptation de la méthode de vote, SQL delta, exécution, tests, rapport et préparation de publication |
| Membres humains du binôme B | Noms, relecture et contributions personnelles à renseigner par les personnes concernées ; non attribués arbitrairement |
| Binômes A et C du groupe | Travail non consulté et non évalué dans ce dépôt |

Les prompts expérimentaux sont retrouvés et vérifiés, sans changement ni nouvel appel en
TD2 ; voir [prompts/README.md](../prompts/README.md). Le prompt de demande d'assistance est
également conservé. Aucun résultat de plénière, note ou quiz n'est inventé.

Cette version séparée doit être relue et expliquée par les étudiants. Pour la remise globale,
intégrer B avec les parties A/C dans le dépôt commun TD1–TD3, compléter les contributions
humaines, puis remettre l'URL, le hash complet et le lien du rapport au commit dans Moodle.
L'échéance officielle est le **22 novembre 2026 à 23 h 59, heure de Paris**. Aucune remise
Moodle n'a été effectuée par cette tâche. Voir [REMISE.md](../REMISE.md) pour l'état de publication.

## 9. Conformité du livrable B

| Exigence de l'étape B | Preuve |
|---|---|
| Chercher sur les cinq modèles et 100 cellules | `final-100-cells.csv`, `shared-wrong-values.json` |
| Identifier le cas, la nature et les modèles | Sections 2–3, `c02-traces.csv` |
| Référence indépendante | Requête TD1, corrigé officiel et calcul Python/CSV, section 6 |
| Déclarer panel et seuil ; comparer 2/3 et 3/5 | Section 3, `quorums.json`, sortie de l'atelier officiel |
| Deux SQL complets, cause exacte du WHERE/JOIN | Section 4, `sql/m1-gpt20b.sql`, `sql/m2-dots.sql` |
| SELECT delta sur la vraie base, identifiants et revenus | Section 5, `sql/delta-c02.sql`, `delta-c02.csv` |
| Expliquer tout l'écart en centimes | Somme 590320 pour les deux modèles, assertions et tests |
| Rapport, code, prompts et preuves reproductibles | Ce rapport, `reproduce.py`, README et dossiers associés |
| Contributions et limites honnêtes | Sections 7–8 ; relecture humaine à réaliser |
