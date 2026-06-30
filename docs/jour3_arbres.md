# Jour 3 — Étage des arbres (PIVOT du projet)

**Module :** `formlang/tree.py` (BUTA générique)
**Apps :** `apps/morpho/automaton.py`, `apps/shield/decomposer.py`
**Tests cibles :** `tests/test_tree.py`

## Pourquoi c'est le pivot

Le **même** `formlang.tree.TreeAutomaton` sert la morphologie **et** le Shield :
seules changent les règles `Δ`. C'est la démonstration concrète que
« automate d'arbres » est une abstraction réutilisable.

## À faire

1. **`tree.py`** : `Term`, `run` (post-ordre, O(|t|)), `accepts`, `product`
   (intersection = états-paires).
2. **`morpho/automaton.py`** : règles `prefix*/root/suffix*` ; `classify` →
   BARE / SUFFIXED / PREFIXED / CIRCUMFIXED.
3. **`shield/decomposer.py`** : états `safe < ovr < role < danger` ; règles
   `seq` (danger remonte ; ovr+role ⇒ danger ; sinon sévérité max),
   `frame`/`sys` (contenu non-safe ⇒ danger).

## Théorie à rédiger

- **Pourquoi un AFD de mots échoue** sur « un `role` **à l'intérieur** d'un
  bloc système » : il faut suivre une **profondeur d'imbrication** non bornée
  (pile / arbre), hors de portée d'une mémoire bornée.
- **Théorème du yield** (admis) : la frontière d'un langage d'arbres régulier
  est **hors-contexte**. Illustrer avec les frontières de `sys(role)`,
  `seq(frame(ovr),txt)`, etc., et relier à la grammaire du jour 2.
- **Clôture par intersection** : justifier la construction `product`.

## Démonstration de fin de journée

Montrer, côte à côte, que `morpho_automaton()` et `shield_automaton()` sont
deux instances de la **même** classe `TreeAutomaton`.

## Critère de fin de journée

`pytest tests/test_tree.py -q` au vert (morpho + shield + produit).

