<!-- Charte IUT/IFRI — bleu #1A3A6B / orange #E07B20 -->

# Jour 5 — Intégration, Myhill–Nerode & ouverture

**Module produit :** `pipeline.py`, `formlang/myhill_nerode.py`
**Tests cibles :** `tests/test_pipeline.py`, `tests/test_cfg_nerode.py`
**Barème du jour :** 3 pts (+2 bonus)

---

## Contexte — recoller les morceaux

Quatre jours durant, vous avez monté la hiérarchie de Chomsky **un étage à la
fois**. Aujourd'hui, deux objectifs : (1) **assembler** les couches en une seule
chaîne de traitement (`pipeline.py`), preuve vivante que les apps **réutilisent**
le cœur ; (2) revenir sur un fil **transversal** qui traverse tout le projet —
la **congruence de Myhill–Nerode**, qui explique *pourquoi* l'AFD minimal du jour
1 a exactement le nombre d'états qu'il a, et qui se prolonge jusqu'aux arbres.

C'est aussi le jour où l'on **mesure** (compression, classes) et où l'on
**finalise** rapport et soutenance.

---

## A. Intégration — 1,5 pt

**E5.1 — Pipeline bout-en-bout (`pipeline.py`) (1 pt).**
Implémenter / vérifier les trois modes, chacun **enchaînant des couches du
cœur** :
- `--word w` : **normaliser** (FST, jour 1) → **détecter `or`** (AFD, jour 1) →
  **délimiteurs** (PDA, jour 2) ;
- `--morpho w` : **segmenter** (heuristique) puis **classer** (BUTA, jour 3) ;
- défaut : démo **Shield** (AttackDecomposer, jour 3).

Faire passer `tests/test_pipeline.py`. Exemple à reproduire :

```text
$ python pipeline.py --word 4or
               entrée : 4or
       normalisé(FST) : aor
      facteur_or(AFD) : True
  délimiteurs_ok(PDA) : True
```

**E5.2 — Étude de cas morphologie sur corpus (0,5 pt).**
Avec `apps/morpho/corpora.py`, générer le corpus **suffixant** (B) et le corpus
**préfixant** (A), puis **classer** quelques formes et vérifier la vérité-terrain :

```python
analyze_morpho("fafak",    set(corpus_B()))  # BARE
analyze_morpho("fafaklar", set(corpus_B()))  # SUFFIXED
analyze_morpho("mufafak",  set(corpus_A()))  # PREFIXED
```

Commenter (rapport) : l'heuristique de découverte d'affixes **sur-génère**-t-elle
(un affixe parasite) ? Reporter les **vrais** chiffres.

---

## B. Myhill–Nerode — le fil transversal — 1,5 pt

**Q5.1 — Définition (0,5 pt).**
Rappeler la congruence `∼_L` : `u ∼_L v` ssi pour tout suffixe `s`,
`(u·s ∈ L) ⟺ (v·s ∈ L)`. Montrer qu'elle est **invariante à droite**.

**Q5.2 — Classes de `L₁` ↔ AFD minimal (0,5 pt).**
Pour `L₁` (facteur `or`, jour 1), déterminer les **classes d'équivalence** de
`∼_{L₁}`. Combien y en a-t-il ? Les relier aux **3 états** de l'AFD minimal du
jour 1 (théorème de Myhill–Nerode : indice de `∼_L` = nombre d'états du minimal).
Interprétation des trois classes :
- mots **sans** facteur `or` et **non armés** (ne finissant pas par `o`) ;
- mots **sans** `or` mais **armés** (finissant par `o`, en attente d'un `r`) ;
- mots contenant **déjà** `or` (classe absorbante).

**E5.3 — Vérification en code (0,5 pt).**
Avec `formlang.myhill_nerode.nerode_classes`, regrouper un échantillon de mots
par signature d'acceptation sur un jeu de **suffixes témoins** et vérifier qu'on
obtient **3 classes**.

> ⚠️ Cette vérification suppose des suffixes témoins **distinguants**. Si deux
> classes fusionnent dans votre test, **ajoutez un suffixe** qui les sépare (par
> exemple un témoin sur lequel un mot « armé » et un mot « non armé » diffèrent).
> C'est le genre d'assertion à **confirmer à l'exécution**, pas à supposer.

---

## C. Ouverture (à rédiger, non noté séparément)

**Q5.4 — Forme canonique des arbres.**
La congruence de Myhill–Nerode se transpose aux **arbres** en remplaçant les
« suffixes » par des **contextes** (arbres à trou). En une phrase : qu'est-ce que
serait une **forme canonique** de *prompt* pour le Shield, et à quoi servirait-elle
(décider une seule fois pour toute une classe d'arbres structurellement
équivalents) ?

---

## D. Bonus — 2 pts

**E5.5 — Hash-consing (+1).**
Compacter une forêt morphologique en **DAG** : interner chaque sous-arbre
structurellement identique sous un identifiant unique. Mesurer
`compression = 1 − uniques/total` sur le corpus. Question : sur quelles langues
(isolantes vs **agglutinantes**) attend-on **le plus** de partage suffixal ?
*(Reporter le vrai taux, même modeste.)*

**Q5.6 — Minimisation transversale (+1).**
Énoncer le parallèle : minimisation d'AFD (fusion des états indistinguables) ↔
minimisation de BUTA (quotient par la congruence des arbres). Décrire l'analogie
point par point (pas d'implémentation requise).

---

## Sorties console attendues (référence)

```text
$ pytest -q
............................                                    [100%]
28 passed
```

*(Le nombre exact de tests dépend de votre arborescence ; l'important est que
tout soit vert.)*

```text
$ python pipeline.py --morpho mufafak
{'mot': 'mufafak', 'classe(BUTA)': 'PREFIXED'}
```

---

## Mini-barème du jour (3 pts + 2 bonus)

| Item | Détail | Pts |
|---|---|---:|
| E5.1 | pipeline 3 modes (réutilise les 4 couches) | 1 |
| E5.2 | étude de cas morpho sur corpus + commentaire | 0,5 |
| Q5.1 | définition `∼_L` + invariance à droite | 0,5 |
| Q5.2 | classes de `L₁` ↔ AFD minimal | 0,5 |
| E5.3 | vérification `nerode_classes` (3 classes) | 0,5 |
| **Bonus** | hash-consing + analyse compression | +1 |
| **Bonus** | minimisation transversale (AFD ↔ BUTA) | +1 |

> *Gate :* `pipeline.py` doit **appeler les apps**, qui elles-mêmes
> **instancient le cœur**. Aucune logique d'automate réécrite dans le pipeline.
> *Honnêteté :* reporter les **vrais** chiffres (tests, compression).

---

## Clôture du projet — ce que vous avez démontré

| Étage | Reconnaît | Mémoire | Le voit échouer sur… |
|---|---|---|---|
| AFD (j1) | un **motif** | bornée (états finis) | l'imbrication non bornée |
| PDA (j2) | une **imbrication** | pile (LIFO) | l'égalité de deux copies |
| BUTA (j3) | une **structure d'arbre** | finie sur états, structure portée par l'arbre | la réduplication non bornée |
| MT / MTU (j4) | **tout le calculable** | ruban non borné | rien… mais **indécidabilité de l'arrêt** |

> Le fil rouge, vérifié en code : *plus la structure est riche, plus il faut de
> mémoire — et au sommet, on gagne l'universalité mais on perd la décidabilité.*

---

## Références

- Hopcroft, Motwani, Ullman — Myhill–Nerode, minimisation d'AFD.
- Comon *et al.*, *TATA* (2007) — minimisation des automates d'arbres
  (congruence sur les contextes), clôtures.
- Daciuk *et al.* (2000) ; Filliâtre & Conchon (2006) — dictionnaires minimaux
  et hash-consing (bonus E5.5).

*Fin du jour 5 — finalisez le rapport (`RAPPORT_TEMPLATE.md`) et la soutenance.*
