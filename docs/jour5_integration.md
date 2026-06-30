# Jour 5 — Intégration, Myhill–Nerode, ouverture

**Modules :** `pipeline.py`, `formlang/myhill_nerode.py`
**Tests cibles :** `tests/test_pipeline.py`, `tests/test_cfg_nerode.py`

## Objectifs

- **`pipeline.py`** : enchaîner les couches sur une entrée :
  `--word` → normaliser (FST) → détecter `or` (AFD) → délimiteurs (PDA) ;
  `--morpho` → segmenter puis **classer** (BUTA) ; démo Shield par défaut.
- **Myhill–Nerode** : classes d'équivalence de `L₁` (facteur `or`) reliées au
  nombre d'états de l'AFD **minimal** du jour 1.

## À faire

1. Vérifier la chaîne bout-en-bout (`test_pipeline.py`).
2. **`myhill_nerode.py`** : `nerode_classes(accepts, mots, suffixes)` →
   regrouper par signature d'acceptation. Attendu pour `L₁` : **3 classes**
   (= 3 états de l'AFD minimal). *Si une classe fusionne, ajouter un suffixe
   témoin distinguant.*

## Théorie à rédiger

- Définition de `∼_L` (invariante à droite) ; **Myhill–Nerode** : indice de
  `∼_L` = nombre d'états de l'automate minimal.
- **Ouverture arbres** : la congruence se transpose aux **contextes** (arbres à
  trou) ; une « forme canonique » de prompt serait son arbre minimal modulo
  cette congruence.

## Bonus

- **Hash-consing** : compacter une forêt morphologique en DAG, mesurer
  `1 − uniques/total`. Plus de partage attendu sur langues **agglutinantes**.
- **Statistiques de corpus** : classer tout `corpus_A`/`corpus_B` et vérifier
  la vérité-terrain (A préfixant, B suffixant).

## Critère de fin de journée

`pytest -q` **complet** au vert ; `pipeline.py` fonctionnel ; rapport finalisé.

