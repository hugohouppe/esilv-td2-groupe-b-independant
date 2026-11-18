# Annexe — contrôle des votes pour le groupe B

Cette annexe est un appui au diagnostic B, calculé à partir des traces TD1 conservées.
Le panel fixe 2/3 est GPT-OSS 120B / Cohere / Qwen ; le panel 3/5 ajoute GPT-OSS 20B et Dots.
Les abstentions ne sont ni correctes ni incorrectes ; `max voix` indique le groupe le plus
nombreux même si le quorum n'est pas atteint. Montants en centimes HT.

| Cas | Référence | Décision 2/3 | Valeur | Max voix | Conforme | Décision 3/5 | Valeur | Max voix | Conforme |
|---|---:|---|---:|---:|---|---|---:|---:|---|
| C01 | 792800 | consensus | 792800 | 3 | oui | consensus | 792800 | 5 | oui |
| C02 | 590320 | consensus | 590320 | 2 | oui | abstention | — | 2 | — |
| C03 | 936350 | consensus | 936350 | 3 | oui | consensus | 936350 | 5 | oui |
| C04 | 2826250 | consensus | 2826250 | 3 | oui | consensus | 2826250 | 5 | oui |
| C05 | 38480 | consensus | 38480 | 3 | oui | consensus | 38480 | 5 | oui |
| C06 | 0 | consensus | 0 | 3 | oui | consensus | 0 | 5 | oui |
| C07 | 13970 | consensus | 13970 | 3 | oui | consensus | 13970 | 5 | oui |
| C08 | 605580 | consensus | 605580 | 3 | oui | consensus | 605580 | 4 | oui |
| C09 | 487980 | consensus | 487980 | 2 | oui | consensus | 487980 | 3 | oui |
| C10 | 558980 | consensus | 558980 | 2 | oui | consensus | 558980 | 3 | oui |
| C11 | 446690 | consensus | 446690 | 2 | oui | consensus | 446690 | 3 | oui |
| C12 | 1666490 | consensus | 1666490 | 3 | oui | consensus | 1666490 | 5 | oui |
| C13 | 107740 | consensus | 107740 | 3 | oui | consensus | 107740 | 5 | oui |
| C14 | 0 | consensus | 0 | 3 | oui | consensus | 0 | 5 | oui |
| C15 | 168680 | abstention | — | 1 | — | abstention | — | 2 | — |
| C16 | 376740 | consensus | 376740 | 2 | oui | consensus | 376740 | 3 | oui |
| C17 | 258180 | abstention | — | 1 | — | abstention | — | 2 | — |
| C18 | 62480 | consensus | 62480 | 2 | oui | consensus | 62480 | 4 | oui |
| C19 | 1990 | abstention | — | 1 | — | consensus | 1990 | 3 | oui |
| C20 | 1106090 | consensus | 1106090 | 2 | oui | consensus | 1106090 | 4 | oui |

Les deux panels retiennent chacun 17 réponses correctes et s'abstiennent trois fois,
mais pas sur les mêmes questions. Aucun des deux ne conserve une réponse fausse sur ce lot.
Cela décrit ce lot ; cela ne mesure pas une fiabilité générale.

## Changements de décision

- **C02 : consensus correct → abstention.** Le panel fixe a 120B=590320 correct,
  Cohere=2606320 incorrect et Qwen=590320 correct. Ajouter 20B=0 incorrect et Dots=0 incorrect
  laisse deux voix pour 590320, deux pour 0 et une pour 2606320. Aucune valeur n'atteint 3.
- **C19 : abstention → consensus correct.** Le panel fixe a 120B=1990 correct,
  Cohere=71640 incorrect et Qwen=83580 incorrect. Ajouter 20B=1990 correct et Dots=1990 correct
  porte la bonne valeur à trois voix.

## Décisions stables et marges

- C01, C03, C04, C05, C06, C07, C12, C13 et C14 : les deux modèles ajoutés donnent chacun
  la référence ; la marge passe de 3 voix sur 3 à 5 sur 5. Les valeurs exactes figurent dans
  le tableau et le fichier de détail ci-dessous. Les références nulles C06 et C14 sont bien
  des valeurs 0, pas des absences de vote.
- C08 : 605580 passe de 3 à 4 voix ; 20B ajoute 605580 correct, Dots donne 186340 incorrect.
- C09 : 487980 passe de 2 à 3 voix avec 20B ; Cohere est `sql_invalid` (valeur absente),
  Dots donne 369240 incorrect. L'erreur SQL reste dans le dénominateur.
- C10 : 558980 passe de 2 à 3 voix avec 20B ; Cohere donne 119410 incorrect, Dots 0 incorrect.
- C11 : 446690 passe de 2 à 3 voix avec 20B ; Cohere donne 666620 incorrect,
  Dots est `sql_rejected` (valeur absente).
- C15 : abstention dans les deux panels. 120B=168680 correct, Cohere=314020 incorrect,
  Qwen=0 incorrect ; 20B ajoute 168680 correct et Dots donne 138920 incorrect. Le maximum
  passe de 1 à 2 voix, toujours sous le seuil.
- C16 : 376740 passe de 2 à 3 voix avec 20B ; Qwen donne 367050 incorrect,
  Dots 211260 incorrect, Cohere donne bien 376740 correct.
- C17 : abstention dans les deux panels. 120B=258180 correct, Cohere=371990 incorrect,
  Qwen=248490 incorrect ; 20B ajoute 258180 correct et Dots donne 152730 incorrect.
  Le maximum passe de 1 à 2 voix, toujours sous le seuil.
- C18 : 62480 passe de 2 à 4 voix, grâce à 20B et Dots ; Qwen est `not_executed`, HTTP 429.
- C20 : 1106090 passe de 2 à 4 voix, grâce à 20B et Dots ; Qwen est `not_executed`, HTTP 429.

Le détail exact des valeurs et verdicts de chaque cellule est conservé dans
[quorums-20.csv](../evidence/quorums-20.csv), et les 100 lignes sélectionnées dans
[final-100-cells.csv](../evidence/final-100-cells.csv). Les références ne sont consultées
qu'après le vote. Aucun appel réseau n'a été effectué.
