# Rapport de projet — formlang

**Binôme :** NOM Prénom 1 · NOM Prénom 2
**Dépôt Git :** <url>   ·   **Commit final :** <hash>

> Reporter les **vrais** chiffres de votre sortie. Toute borne de complexité
> doit être démontrée ou **référencée** (pas de constante « de mémoire »).

## 0. Résumé (½ page)

Ce que fait le projet, l'architecture en une phrase, le résultat global de
`pytest` (copier la ligne `N passed`).

## 1. Étage régulier & transducteurs (Jour 1)

- AFD de `L₁`, table de transition, **minimalité** (justification).
- regex → AFN → AFD → minimal.
- Idempotence du FST leet (preuve).
- Miroir : one-way impossible / two-way possible (argument mémoire bornée).

## 2. Hors-contexte (Jour 2)

- Preuve de non-régularité de `{[ⁿ]ⁿ}` (pompage).
- Grammaire des prompts bien parenthésés ; ambiguïté + désambiguïsation.
- PDA : fonction de transition.

## 3. Arbres (Jour 3) — pivot

- BUTA : définition utilisée, règles Δ morpho et Δ shield.
- **Preuve d'unité** : capture d'écran/extrait montrant que les deux apps
  instancient `formlang.tree.TreeAutomaton`.
- Pourquoi un AFD de mots échoue ; théorème du yield ; produit (intersection).
- Traces : exécution ascendante sur 2–3 arbres (état par nœud).

## 4. Calculabilité (Jour 4)

- MT générique : invariant, trace d'une exécution.
- MTU : encodage, vérification `U(⟨M⟩##w) == M(w)`.
- Calculatrice : tables ADD/SUB **expliquées ligne par ligne** ; MUL/DIV par
  composition. Résultats des tests exhaustifs.
- Surcoût de simulation (sourcé) ; indécidabilité de l'arrêt.

## 5. Intégration & Myhill–Nerode (Jour 5)

- `pipeline.py` : un exemple bout-en-bout commenté.
- Classes d'équivalence de `L₁` ; lien avec l'AFD minimal.
- (Bonus) hash-consing : `total / uniques / compression` mesurés.

## 6. Difficultés rencontrées & choix de conception

Ce qui a résisté, ce que vous auriez fait autrement.

## 7. Répartition du travail

Qui a fait quoi (par module).

## Annexe — sortie console

Coller `pytest -q` complet et `python pipeline.py` (3 modes).

