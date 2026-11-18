# Expliquer le groupe B

## Présentation courte

Nous avons recherché une valeur fausse partagée dans les 100 cellules finales du TD1.
Il y a 106 lignes parce que six lignes sont des reprises, pas des votes supplémentaires.
Le seul cas partagé est C02 : GPT-OSS 20B et Dots donnent zéro alors que la référence vaut
590 320 centimes. Nous avons rejoué ces requêtes sur la base officielle.

GPT-OSS 20B cherche des personnes nées en 2025–2026 : ce ne sont pas les clients de 25 ans.
Dots ne garde que les clients dont c'est exactement le 25e anniversaire, puis impose des
commandes le 25 septembre, alors que la question demande toutes leurs commandes.
La base s'arrête au 20 septembre ; sa requête n'a donc aucune ligne à additionner.

Le bon intervalle de naissance est strictement après le 25 septembre 2000 et jusqu'au
25 septembre 2001 inclus. Notre diagnostic trouve six clients, soit 82 lignes de commande,
pour 590 320 centimes. Un calcul indépendant sur les CSV retrouve les mêmes montants.

Le panel officiel 120B/Cohere/Qwen vote deux fois pour la bonne réponse. À cinq, il y a
deux bonnes réponses, deux zéros et une troisième valeur : personne n'atteint trois voix.
L'accord entre deux modèles est donc réel, mais il ne gagne pas ces panels officiels.

## Questions à maîtriser

- **Pourquoi une borne ouverte et l'autre fermée ?** Né le 25/09/2000, on a déjà 26 ans.
  Né le 25/09/2001, on vient d'avoir 25 ans. Né le 26/09/2001, on n'a encore que 24 ans.
- **Pourquoi ne pas compter trois erreurs comme trois voix ?** On vote pour une valeur exacte.
  Zéro et 2 606 320 sont des votes différents.
- **Pourquoi conserver les erreurs dans n ?** Une indisponibilité ne doit pas abaisser le
  seuil de confiance. Deux valeurs égales sur cinq ne suffisent pas pour k=3.
- **Que signifie `votes=2` lors de l'abstention ?** C'est la taille du plus grand groupe,
  pas la preuve qu'une valeur a gagné ; la valeur retournée reste `None`.
- **Pourquoi `COALESCE` ?** `SUM` sur zéro ligne vaut `NULL` ; `COALESCE(...,0)` donne zéro.
  Cela respecte le format de sortie mais masque l'erreur de sélection.
- **Pourquoi 82 lignes et non 82 commandes ?** Une commande peut avoir plusieurs produits.
  La clé de la ligne est `(order_id, product_id)`.
- **Le vote connaît-il le corrigé ?** Non. La comparaison à la référence vient après la décision.
- **Peut-on généraliser le taux observé ?** Non : une base, vingt questions et des modèles
  pouvant partager leurs erreurs ne donnent pas une garantie d'exactitude future.
- **Que reste-t-il au groupe ?** Relire et expliquer, ajouter les contributions humaines,
  assembler A/B/C dans le dépôt commun et effectuer la remise Moodle.
