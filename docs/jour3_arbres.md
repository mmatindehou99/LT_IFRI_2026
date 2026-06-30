<!-- Charte IUT/IFRI — bleu #1A3A6B / orange #E07B20 -->

# Jour 3 — 🌳 Automates d'arbres : le cœur du projet

**Module produit :** `formlang/tree.py` (BUTA générique)
**Applications :** `apps/morpho/automaton.py`, `apps/shield/decomposer.py`
**Tests cibles :** `tests/test_tree.py`
**Barème du jour :** 5 pts (+2 bonus)

> ⚠️ **Cadre éthique.** Le volet Shield reste 100 % structurel : feuilles
> abstraites `txt, enc, ovr, role`, nœuds `seq, sys, frame`. Aucune attaque
> réelle.

---

## Contexte — pourquoi c'est le pivot

Hier, la **pile** comptait une profondeur d'imbrication *pendant* une lecture
linéaire. Aujourd'hui, on franchit un cap : on ne lit plus un mot, on lit un
**arbre**, et l'imbrication y est **native**. Un automate d'arbres décide donc
trivialement des propriétés que l'AFD ne savait pas exprimer — par exemple
« un `role` apparaît **à l'intérieur** d'un bloc système ».

C'est aussi le moment où le projet prouve son **unité** : un **seul** moteur
(`formlang.tree.TreeAutomaton`) sert **deux** applications très différentes —
l'analyse **morphologique** et le **Shield défensif**. Seules changent les
règles `Δ`. Si vous écrivez deux automates d'arbres distincts, vous avez raté
l'objectif du jour.

Rappel du pont (jours 1–2) : un mot est un arbre dégénéré (branche unaire) ;
un AFD est le cas « tout en arité 1 ». L'automate d'arbres **généralise**
l'automate fini.

---

## Rappels formels

Un **automate d'arbres ascendant déterministe** (BUTA) est `A = (Q, F, Δ)` sur un
alphabet **gradué** : chaque symbole apparaît avec une arité (distinguée par le
nombre d'enfants dans `Δ`). Les règles ont la forme
f(q₁, …, qₖ) → q        (feuille : a() → q)

L'exécution `run` étiquette l'arbre **des feuilles vers la racine** (post-ordre) :
`run(f(t₁,…,tₖ)) = q` si `run(tᵢ)=qᵢ` pour tout `i` et `f(q₁,…,qₖ)→q ∈ Δ` ;
sinon `REJECT`. L'arbre est **accepté** ssi `run(racine) ∈ F`. Coût `O(|t|)`.

---

## A. Théorie (à rédiger) — 2 pts

**Q3.1 — Déterminisme & complétude (0,5 pt).**
Pour l'automate **morphologique** (§B.1) **et** pour l'automate **Shield**
(§B.2), dire s'ils sont **déterministes** (au plus une règle par membre gauche
`f(q₁,…,qₖ)`) et **complets** (au moins une). Justifier en inspectant les
règles.

**Q3.2 — Pourquoi un AFD de mots échoue (0,5 pt).**
Expliquer pourquoi la propriété « un `role` apparaît **à l'intérieur** d'un bloc
système `sys(…)` » **ne peut pas** être décidée par un AFD lisant le mot de
gauche à droite, alors qu'elle l'est trivialement par l'automate d'arbres.
*(Relier à la profondeur d'imbrication non bornée du jour 2.)*

**Q3.3 — Théorème du yield / frontière (0,5 pt).**
On **admet** que la **frontière** (mot des feuilles, de gauche à droite) d'un
langage d'arbres régulier est un langage **hors-contexte**. Donner la frontière
des trois termes de **E3.4** ci-dessous, et expliquer le lien avec la grammaire
du jour 2.

**Q3.4 — Réduplication, non-régularité (0,5 pt).**
La **réduplication** (copier une partie de longueur **arbitraire** de la racine,
type `ww`) est-elle un langage d'arbres **régulier** ? Justifier par l'argument
de **mémoire bornée** (un BUTA a un nombre fini d'états : il ne peut pas comparer
l'égalité de deux sous-arbres de taille non bornée).

---

## B. Pratique — 2,5 pts

Le cœur `formlang/tree.py` fournit `Term`, `run`, `accepts`, `product`. **Les
applications l'instancient — elles ne le réécrivent pas.**

**E3.1 — `run` et `accepts` du BUTA (1 pt).**
Vérifier (ou compléter) `TreeAutomaton.run` (post-ordre, propagation de
`REJECT`) et `accepts`. Le test `tests/test_tree.py` doit passer.

**E3.2 — Automate morphologique (`apps/morpho/automaton.py`) (0,75 pt).**
Instancier un `TreeAutomaton` reconnaissant `word(prefixes*, rest(root,
suffixes*))`, puis `classify` → **BARE / SUFFIXED / PREFIXED / CIRCUMFIXED**.
Vérifier :

```python
classify(A, build_word([],       "livre", []))    # BARE
classify(A, build_word([],       "jou",   ["er"])) # SUFFIXED
classify(A, build_word(["na"],   "penda", []))     # PREFIXED
classify(A, build_word(["a","na"],"pend", ["a"]))  # CIRCUMFIXED
```

Règles attendues (`Δ` morphologique) :
feuilles :  prefix→PRE  root→ROOT  suffix→SUF  nil→NIL
chaînes  :  suffixes(SUF,SUFS|NIL)→SUFS    prefixes(PRE,PREFS|NIL)→PREFS
reste    :  rest(ROOT,SUFS|NIL)→REST
mot      :  word(PREFS|NIL, REST)→WORD          F = { WORD }
**E3.3 — AttackDecomposer (`apps/shield/decomposer.py`) (0,75 pt).**
Instancier **le même** `TreeAutomaton` avec les règles défensives. États
`safe < ovr < role < danger` ; `F = { danger }` (accepter = **bloquer**).
feuilles :  txt,enc → safe     ovr → ovr      role → role
seq      :  danger remonte ; {ovr,role} → danger ; sinon sévérité max
frame/sys:  contenu non-safe → danger ; safe → safe
Vérifier :

```python
is_blocked(A, seq(txt(), txt()))               # False
is_blocked(A, role())                          # False  (rôle isolé : OK)
is_blocked(A, sys(role()))                     # True
is_blocked(A, seq(frame(ovr()), txt()))        # True
is_blocked(A, sys(seq(txt(), frame(role()))))  # True
is_blocked(A, seq(ovr(), role()))              # True   (annulation + rôle)
```

> **Lecture sémantique.** Un `ovr` ou un `role` **isolé** n'est pas bloqué (un
> utilisateur peut légitimement écrire « ignore le bruit » ou « joue un rôle »).
> Il devient dangereux **uniquement** imbriqué sous `sys`/`frame`, ou combiné à
> son complément au même niveau. **C'est l'arbre qui décide, pas le jeton.**

**E3.4 — Clôture par intersection (`product`) (inclus, vérifié par test).**
Vérifier que `product(A₁, A₂)` reconnaît `L(A₁) ∩ L(A₂)` (états = paires), sur
deux automates jouets : « nombre **pair** de feuilles `a` » et « **au moins
une** feuille `a` ».

---

## C. La démonstration d'unité (0,5 pt) — à montrer en soutenance

**E3.5 — Preuve d'unité.**
Dans le rapport **et** à l'oral, montrer explicitement que
`morpho_automaton()` et `shield_automaton()` renvoient **deux instances de la
même classe** `formlang.tree.TreeAutomaton`, ne différant **que** par leurs
règles `Δ` et leurs états finaux. C'est l'objectif central de la journée.

---

## Trace ascendante de référence (à reproduire dans le rapport)

Terme `sys(seq(txt, frame(role)))` (Shield) — étiquetage **feuilles → racine** :

| nœud | règle appliquée | état |
|---|---|---|
| `txt` | `txt → safe` | safe |
| `role` | `role → role` | role |
| `frame(role)` | `frame(role) → danger` | **danger** |
| `seq(txt, frame…)` | `seq(safe, danger) → danger` | **danger** |
| `sys(seq…)` | `sys(danger) → danger` | **danger** |

Racine = `danger ∈ F` ⇒ **BLOQUÉ**.

Terme morphologique `word(prefixes(a, prefixes(na, nil)), rest(root(pend),
suffixes(a, nil)))` :

| nœud | règle | état |
|---|---|---|
| `prefix(a)`, `prefix(na)` | `prefix → PRE` | PRE |
| `nil` | `nil → NIL` | NIL |
| `prefixes(na, nil)` | `prefixes(PRE,NIL) → PREFS` | PREFS |
| `prefixes(a, …)` | `prefixes(PRE,PREFS) → PREFS` | PREFS |
| `root(pend)` | `root → ROOT` | ROOT |
| `suffix(a)` / `nil` | feuilles | SUF / NIL |
| `suffixes(a, nil)` | `suffixes(SUF,NIL) → SUFS` | SUFS |
| `rest(root, suffixes)` | `rest(ROOT,SUFS) → REST` | REST |
| `word(prefixes, rest)` | `word(PREFS,REST) → WORD` | **WORD** |

Racine = `WORD ∈ F` ⇒ **ACCEPTÉ**, classe **CIRCUMFIXED** (préfixe ∧ suffixe).

---

## Sorties console attendues (référence)

```text
$ pytest -q tests/test_tree.py
.....                                                           [100%]
5 passed
```

```text
$ python pipeline.py
== démo Shield (AttackDecomposer) ==
  OK      seq(txt,txt)
  OK      role (isolé)
  BLOQUÉ  sys(role)
  BLOQUÉ  seq(frame(ovr),txt)
  BLOQUÉ  sys(seq(txt,frame(role)))
```

---

## Mini-barème du jour (5 pts + 2 bonus)

| Item | Détail | Pts |
|---|---|---:|
| Q3.1 | déterminisme & complétude (morpho + shield) | 0,5 |
| Q3.2 | pourquoi un AFD échoue | 0,5 |
| Q3.3 | théorème du yield + frontières | 0,5 |
| Q3.4 | réduplication non régulière (mémoire bornée) | 0,5 |
| E3.1 | `run`/`accepts` du BUTA | 1 |
| E3.2 | automate morphologique + `classify` | 0,75 |
| E3.3 | AttackDecomposer | 0,75 |
| E3.5 | preuve d'unité (même classe, deux Δ) | 0,5 |
| **Bonus** | produit/intersection démontré + **infixation** (étendre `Δ` pour `s<um>ulat`) | +1 |
| **Bonus** | **minimisation** d'un BUTA (quotient par congruence des arbres) | +1 |

> *Gate (le plus important du projet) :* les deux apps doivent **instancier**
> `formlang.tree.TreeAutomaton`. Toute app qui **réimplémente** un automate
> d'arbres perd l'intégralité des points d'intégration du projet.

---

## Références

- Comon *et al.*, *TATA — Tree Automata Techniques and Applications* (2007),
  ch. 1 : BUTA, déterminisme, clôtures (intersection par produit), minimisation.
- Gécseg & Steinby, *Tree Automata* (1984 ; rééd. 2015).
- Roche & Schabes (dir.), *Finite-State Language Processing* (1997) — morphologie
  à états finis.

*Fin du jour 3 → passez à `jour4_calculabilite.md`.*
