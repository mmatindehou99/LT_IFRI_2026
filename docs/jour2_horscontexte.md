# Jour 2 — Étage hors-contexte

**Modules :** `formlang/pda.py`, `formlang/cfg.py` (bonus)
**App :** `apps/shield/delimiters.py`
**Tests cibles :** `tests/test_cfg_nerode.py`, `tests/test_regular.py::*delimiters*`

## Objectifs

- Automate à pile (acceptation **pile vide**) pour `[] ()` bien imbriqués.
- Grammaire hors-contexte des prompts bien parenthésés ; génération bornée.

## À faire

1. **`delimiters.py`** : `well_parenthesized(w)` via `DelimiterPDA`
   (empile ouvrants, dépile sur fermant correspondant, ignore `a o r e`).
2. **`cfg.py`** : `balanced_cfg()` = `S → S S | [S] | (S) | a | o | r | ε` ;
   `generate(max_len)` énumère les mots terminaux ≤ longueur donnée.

## Théorie à rédiger

- **Non-régularité de D = { [ⁿ ]ⁿ }** par le **lemme de l'étoile** : avec
  w = [ᵖ]ᵖ, toute coupe xyz (|xy| ≤ p, |y| ≥ 1) a y ⊆ bloc de `[`, donc
  xy²z déséquilibré ∉ D. ⇒ un AFD **ne peut pas** vérifier l'imbrication.
- **Grammaire + ambiguïté** : `S → S S` rend G ambiguë (`aaa` a ≥ 2 arbres) ;
  désambiguïser par `S → T S | T`.
- **PDA** : donner δ (empiler témoin `#[`/`#(`, dépiler si sommet correspond).

## Lien avec la suite

L'imbrication non bornée est exactement ce qu'un **arbre** encode nativement :
le jour 3 reprend ces délimiteurs comme nœuds `sys`/`frame`.

## Critère de fin de journée

`pytest tests/test_cfg_nerode.py -q` (partie CFG) au vert + delimiters verts.

