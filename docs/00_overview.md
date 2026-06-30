# Vue d'ensemble

## Le fil rouge

Une seule question, posée à cinq niveaux de difficulté croissante :
**« reconnaître une structure »**, depuis un facteur dans un mot jusqu'à
n'importe quel calcul. À chaque étage, on observe le même phénomène :

> plus la structure à reconnaître est riche, plus il faut de **mémoire** —
> et il existe un seuil (la machine universelle) où l'on gagne l'universalité
> mais où l'on **perd la décidabilité**.

## Pourquoi « intégrateur » et pas « trois TP » ?

Les trois TP d'origine (morphologie, Shield, MTU) partagent en réalité les
mêmes objets formels. Plutôt que de les réimplémenter trois fois, on construit
**un cœur unique** et on le **réutilise**. Concrètement :

- `apps/morpho` et `apps/shield` instancient **le même** `formlang.tree`
  (BUTA) — seules les règles Δ changent. C'est la preuve vivante que
  « automate d'arbres » est une abstraction, pas un programme jetable.
- `apps/calc` n'écrit aucune boucle d'exécution : il décrit des **tables** et
  les fait tourner par `formlang.turing` / `formlang.utm`.

## Arbre de dépendances (à dessiner au jour 0)
apps/morpho ─┐
apps/shield ─┼─► formlang.tree
apps/shield ─┼─► formlang.dfa, formlang.fst, formlang.pda
apps/calc   ─┴─► formlang.turing ─► formlang.utm
pipeline.py ───► (toutes les apps)


## Compétences évaluées

1. Implémenter ET tester chaque famille d'automate.
2. **Justifier** pourquoi un étage inférieur échoue là où le supérieur réussit
   (pompage, mémoire bornée).
3. **Composer** des reconnaisseurs (produit d'automates, composition de FST,
   sous-machines de Turing).
4. Relier théorie et code par des **traces**.
5. Discuter les **limites** (indécidabilité de l'arrêt).

## Lecture conseillée des fiches

`jour1` régulier+FST → `jour2` hors-contexte → `jour3` arbres (pivot) →
`jour4` calculabilité → `jour5` intégration + Myhill–Nerode.
