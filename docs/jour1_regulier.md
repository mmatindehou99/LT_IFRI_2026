<!-- Charte IUT/IFRI — bleu #1A3A6B / orange #E07B20 -->

# Jour 1 — Étage régulier : automates finis & transducteurs

**Module produit :** `formlang/dfa.py`, `formlang/nfa.py`, `formlang/fst.py`
**Applications :** `apps/shield/detector.py`, `apps/shield/normalizer.py`
**Tests cibles :** `tests/test_regular.py`
**Barème du jour :** 4 pts (+1 bonus)

> ⚠️ **Cadre éthique.** Tout est structurel : on travaille sur l'alphabet
> abstrait `{a, o, r}` (et chiffres *leet*). Aucun contenu réel.

---

## Contexte — pourquoi commencer ici ?

Le premier réflexe d'un système de défense (`SingularityDetector`) est de
repérer un **motif** : par exemple une annulation d'instruction immédiatement
suivie d'une réassignation de rôle. C'est *exactement* « le mot contient le
facteur `or` » — un langage **régulier**, reconnaissable par un automate fini.

Avant de détecter, le système **normalise** le texte (défaire le *leetspeak* :
`4→a`, `0→o`…). Une normalisation lettre à lettre est une **relation
rationnelle**, réalisée par un **transducteur fini**.

Ce jour pose donc l'étage le plus bas de la hiérarchie : ce qu'une **mémoire
bornée** (un nombre fini d'états) suffit à reconnaître — et, en fin de fiche, on
touche déjà sa **limite** (le miroir).

Rappel utile pour la suite : un **mot** `a₁a₂…aₙ` est un **arbre dégénéré**, une
branche unaire `a₁(a₂(…aₙ(⊥)))`. Un automate fini est le cas « tout en arité 1 »
de l'automate d'arbres du jour 3.

---

## A. Théorie (à rédiger dans le rapport) — 2 pts

On pose `Σ = {a, o, r}` et
`L₁ = { w ∈ Σ\* | w contient le facteur « or » }` (un `o` **immédiatement** suivi
d'un `r`).

**Q1.1 — Expression régulière (0,5 pt).**
Donner une expression régulière dénotant `L₁`.

**Q1.2 — AFN → AFD → minimal (1 pt).**
Construire un AFN reconnaissant `L₁` (méthode de Thompson ou directe), le
**déterminiser** (sous-ensembles), puis le **minimiser** (Moore/Hopcroft).
Donner la **table de transition** de l'AFD minimal et **dessiner** l'automate.
Combien d'états ?

**Q1.3 — Facteur vs sous-séquence (0,5 pt).**
Soit `L₁' = { w | w contient un o suivi, pas forcément immédiatement, d'un r }`.
Donner l'expression régulière de `L₁'` et expliquer **en une phrase** la
différence avec `L₁`. Préciser l'inclusion `L₁ ? L₁'`.

> Cible attendue (sans la donner aux étudiants dans l'énoncé distribué) : l'AFD
> minimal de `L₁` a **3 états**.

---

## B. Pratique — 2 pts

Le squelette définit `DFA`, `NFA`, `SequentialFST`. Compléter / exploiter, puis
faire passer `tests/test_regular.py`.

**E1.1 — Détecteur (`apps/shield/detector.py`) (0,75 pt).**
Implémenter `contains_or(w)` **sous forme d'AFD** (table de transition `δ`),
**pas** avec l'opérateur `in` de Python. États : `A` (init), `B` (`o` vu,
« armé »), `C` (accepté, absorbant). Vérifier sur la table ci-dessous.

```
        a            o            r
   A    A            B            A
   B    A            B            C   ← détection : 'o' puis 'r'
   C    C            C            C   ← absorbant (déjà accepté)
init = A   ;   final = { C }
```


**E1.2 — Minimisation (0,25 pt).**
Vérifier en test que `detector_dfa().minimize().num_states() == 3` (cohérent
avec Q1.2).

**E1.3 — Déterminisation AFN→AFD (0,5 pt).**
Construire un AFN (avec `''` pour ε) acceptant les mots **finissant par `b`**,
le convertir avec `to_dfa()`, et vérifier que les **deux acceptent les mêmes
mots** sur un jeu de mots témoins.

**E1.4 — Normaliseur leet (`apps/shield/normalizer.py`) (0,5 pt).**
Implémenter `leet_normalize` via un FST à **un seul état** `q0` (final) :
`4/a 3/e 0/o 1/i 5/s`, identité sinon. Vérifier
`leet_normalize("4tt4ck") == "attack"` et `leet_normalize("r0le") == "role"`.

---

## C. Question d'analyse — la limite du régulier (1 pt)

**Q1.4 — Idempotence du transducteur (0,5 pt).**
Montrer **formellement** que `T(T(w)) = T(w)` pour tout `w`.
*Indication :* l'image de `τ` ne contient **aucun** chiffre *leet*, donc tout
symbole de sortie est un point fixe de `τ` ; comme `T` applique `τ` lettre à
lettre, le résultat est stable.

**Q1.5 — Le miroir `w ↦ wᴿ` (0,5 pt).**
Le Shield gère aussi le **texte inversé**. La transduction miroir est-elle
réalisable par un transducteur fini **à une passe (one-way)** ? Justifier par un
**argument de mémoire bornée** (pour émettre la 1ʳᵉ lettre de sortie — la
dernière lue — il faudrait retenir tout `w`, ce qui croît avec `|w|` ; or les
états sont en nombre fini). Indiquer pourquoi un transducteur **bidirectionnel
(two-way)** y parvient. Dans le code, `reverse_twoway` modélise ce cas.

---

## Sorties console attendues (référence)

```text
$ python pipeline.py --word 4or
               entrée : 4or
       normalisé(FST) : aor
      facteur_or(AFD) : True
  délimiteurs_ok(PDA) : True
```

```text
$ pytest -q tests/test_regular.py
......                                                          [100%]
6 passed
```

---

## Mini-barème du jour (4 pts + 1 bonus)

| Item | Détail | Pts |
|---|---|---:|
| Q1.1 | regex de `L₁` | 0,5 |
| Q1.2 | AFN→AFD→minimal + table + dessin | 1 |
| Q1.3 | `L₁'` (sous-séquence) + différence | 0,5 |
| E1.1 | `contains_or` en AFD (table `δ`) | 0,75 |
| E1.2 | minimisation à 3 états vérifiée | 0,25 |
| E1.3 | déterminisation AFN→AFD équivalente | 0,5 |
| E1.4 | FST leet | 0,5 |
| Q1.4 + Q1.5 | idempotence + miroir one/two-way | inclus ci-dessus (1) |
| **Bonus** | regex → AFN par construction de **Thompson** (module `regex.py`) | +1 |

> *Gate :* `detector.py` doit **instancier `formlang.dfa.DFA`**, pas
> réimplémenter un automate ; sinon les points d'intégration sautent.

---

## Références

- Hopcroft, Motwani, Ullman, *Introduction to Automata Theory* — chap.
  expressions régulières, déterminisation (sous-ensembles), minimisation,
  lemme de l'étoile (utilisé au jour 2).
- Pour les transducteurs et le miroir one-way/two-way : cours sur les
  transductions rationnelles (la non-réalisabilité one-way du renversement est
  classique ; l'argument de mémoire bornée suffit).

*Fin du jour 1 → passez à `jour2_horscontexte.md`.*
