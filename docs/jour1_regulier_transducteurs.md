# Jour 1 — Étage régulier (mots) & transducteurs

**Modules :** `formlang/dfa.py`, `formlang/nfa.py`, `formlang/fst.py`
**Apps :** `apps/shield/detector.py`, `apps/shield/normalizer.py`
**Tests cibles :** `tests/test_regular.py`

## Objectifs

- AFD : `run`, `accepts`, **minimisation** (raffinement de partition / Moore).
- AFN : **déterminisation** par sous-ensembles (avec ε).
- FST séquentiel : transduction lettre à lettre, **composition**, **idempotence**.

## À faire

1. **`detector.py`** : `contains_or(w)` via l'AFD à 3 états (A=init, B='o' vu,
   C=accepté absorbant). Vérifier `minimize().num_states() == 3`.
2. **`normalizer.py`** : `leet_normalize` via `leet_fst()` (4→a, 3→e, 0→o, 1→i,
   5→s ; identité sinon).
3. **NFA→DFA** : vérifier l'équivalence sur des mots témoins.

## Théorie à rédiger (rapport)

- **regex → AFN (Thompson) → AFD (sous-ensembles) → AFD minimal.** Donner la
  table de l'AFD et justifier la minimalité (A, B, C distinguables).
- **Idempotence du FST leet** : l'image de τ ne contient aucun chiffre leet,
  donc τ(τ(x)) = τ(x) lettre à lettre ⇒ T(T(w)) = T(w).
- **Miroir w ↦ wᴿ** : impossible **one-way** (mémoire bornée : retenir tout w
  avant d'émettre la 1ʳᵉ lettre exige un nombre non borné d'états) ; possible
  **two-way**. Le code modélise le miroir comme une opération bidirectionnelle.

## Pièges

- Un AFD **incomplet** n'est pas minimisable directement : `dfa.minimize()`
  ajoute un **puits** avant de raffiner.
- `identity_on_missing=True` ne s'utilise **pas** dans `compose` (il faut des
  tables explicites pour composer).

## Critère de fin de journée

`pytest tests/test_regular.py -q` au vert.

