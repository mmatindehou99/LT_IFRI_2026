# TP — Automates d'arbres : de l'automate fini sur les mots à la reconnaissance de structures

> **Cours** : Théorie des langages — Master Génie Logiciel
> **Pré-requis (acquis)** : langages formels, expressions régulières, grammaires,
> automates finis (AFD/AFN).
> **Concept introduit** : **automates d'arbres** (*tree automata*).
> **Durée** : 1 séance encadrée (≈ 3 h 30) + mini-projet optionnel.
> **Modalités** : binôme. Rendu : rapport PDF + code + tests.
> **Matériel** : paquet autonome (`tree_automaton.hpp`, `ta_check.cpp`,
> `morph_demo.cpp`, `gen_corpora.py`, `Makefile`). Domaine public (CC0).

---

## 0. Objectifs

Vous savez reconnaître un **langage régulier** sur des **mots** avec un **automate
fini**. Ce TP vous fait franchir une marche : reconnaître un langage régulier sur des
**arbres** avec un **automate d'arbres**. On prend comme support concret la
**structure morphologique d'un mot** (`préfixes* racine suffixes*`) — un cas où la
frontière entre « surface » (une chaîne) et « structure » (un arbre) est limpide.

À la fin, vous saurez : (1) définir un alphabet rangé, un terme, un automate d'arbres
ascendant ; (2) dérouler une reconnaissance ascendante à la main ; (3) relier
l'automate d'arbres à l'automate fini (par la *frontière*) ; (4) lire, exécuter et
**étendre** un reconnaisseur d'arbres ; (5) l'appliquer à la segmentation
morphologique et à la classification.

### Mise en route

```sh
make run     # compile tout, génère les corpus, lance les deux démos
```

---

## 0bis. À quoi servent les automates d'arbres ? (situer le sujet)

Un **automate fini** reconnaît des **mots** : des suites *linéaires* de symboles. Or
quantité d'objets que manipule un informaticien ne sont **pas** linéaires — ce sont
des **arbres**. Un **automate d'arbres** est *exactement* ce que devient un automate
fini quand l'entrée est un arbre : un dispositif à **mémoire bornée** (un nombre fini
d'« états ») qui décide, par des **règles locales**, si un arbre appartient à un
ensemble — un *langage d'arbres*. Partout où l'on doit **reconnaître, valider ou
transformer un ensemble d'arbres défini par des règles locales**, c'est l'outil.

| Domaine | L'arbre, c'est… | L'automate d'arbres sert à… |
|---|---|---|
| **Compilation** | l'AST (arbre syntaxique abstrait) | valider la bonne formation ; **sélectionner les instructions** par filtrage d'arbres (générateurs de code *BURS*/twig) ; repérer des motifs d'optimisation |
| **Documents structurés** | XML / JSON / HTML | un **schéma** (DTD, XML Schema, RelaxNG) *est* un langage d'arbres régulier ; un **validateur** *est* un automate d'arbres |
| **Vérification de programmes** | ensembles d'états/termes | *regular tree model checking* : représenter une infinité d'états par un automate d'arbres fini |
| **TAL** | arbre syntaxique, structure d'un mot | valider la structure des phrases et des **mots** (le fil rouge de ce TP) |
| **Réécriture & preuve** | termes | clôturer des ensembles de termes, démonstration automatique |
| **Bases de données** | document XML | évaluer une requête XPath/XQuery = parcours d'automate d'arbres |

**Pour l'ingénieur Génie Logiciel** : chaque fois que vous **validez un document
structuré** (un XML contre son schéma) ou que vous **filtrez des motifs sur un AST**
(un *linter*, un optimiseur, un générateur de code), vous utilisez — souvent sans le
nommer — la théorie des **langages d'arbres réguliers**. Ce TP en donne le socle
formel *et* une implémentation complète et exécutable. *(Réf. : TATA [1] ; schémas
XML [6] ; génération de code par filtrage d'arbres [7].)*

**Pourquoi la morphologie comme fil rouge ?** Parce qu'elle exhibe, sur un exemple
minimal, **la frontière exacte** entre les deux mondes : la *surface* d'un mot est une
**chaîne** (du ressort de l'automate fini), mais sa *structure* — préfixes, racine,
suffixes, emboîtés — est un **arbre** (du ressort de l'automate d'arbres). On voit donc
noir sur blanc **où l'automate fini s'arrête et où l'automate d'arbres prend le relais**.

---

## 1. Rappel et mise en tension (≈ 30 min)

### 1.1 La morphologie de surface est un langage régulier

En surface, un mot fléchi se découpe en `préfixes* racine suffixes*`, sur l'alphabet
des morphèmes `{p = préfixe, r = racine, s = suffixe}`.

> **Exercice 1.1.** Donnez une **expression régulière** décrivant un mot bien formé
> (exactement une racine, entourée d'un nombre quelconque de préfixes et de
> suffixes). Donnez l'**AFD** correspondant (états, transitions, état(s) final/aux) et
> son nombre **minimal** d'états (justifiez par la minimisation).

### 1.2 Là où l'automate fini ne suffit plus

La séquence plate `p p r s` ne dit pas **comment** le mot est construit : quelle est
la tête (`racine`), quel suffixe s'attache en premier, quelle est la sous-structure
`reste = racine + suffixes`. Cette information est **hiérarchique** : un **arbre**.

> **Exercice 1.2.** Soit `a-na-pend-a` (deux préfixes `a`, `na` ; racine `pend` ; un
> suffixe `a`). Dessinez **deux** arbres différents ayant la **même** frontière
> (*yield*) `a na pend a`. Concluez : pourquoi la frontière — ce que lit un automate
> fini — ne caractérise-t-elle pas la structure ?

---

## 2. Automates d'arbres : le cadre (≈ 45 min)

### 2.1 Définitions

**Alphabet rangé** Σ : ensemble fini de symboles, chacun d'une **arité** (`f⁽ⁿ⁾`).
Les symboles d'arité 0 sont les **feuilles**.

**Termes (arbres)** `T_Σ` : plus petit ensemble tel que `f⁽ⁿ⁾ ∈ Σ` et `t₁,…,tₙ ∈ T_Σ`
donnent `f(t₁,…,tₙ) ∈ T_Σ`.

**Automate d'arbres ascendant déterministe** `A = (Q, Σ, Q_f, Δ)` :
`Q` états ; `Q_f ⊆ Q` finaux ; `Δ` règles `f(q₁,…,qₙ) → q`.

**Exécution ascendante** : on étiquette chaque nœud par un état, **des feuilles vers
la racine**. Une feuille `a⁽⁰⁾` reçoit `q` s'il existe `a() → q` ; un nœud
`f(t₁,…,tₙ)` d'enfants `q₁,…,qₙ` reçoit `q` s'il existe `f(q₁,…,qₙ) → q`. L'arbre est
**accepté** ssi la racine reçoit un état de `Q_f`.

> *Analogie* : c'est l'automate fini, mais l'état d'un nœud se calcule en
> **fusionnant les états de ses enfants** (au lieu de suivre une chaîne). Un AFD est
> le cas particulier « arbres unaires » : une chaîne `a₁a₂…aₙ` n'est qu'un arbre où
> chaque nœud a un seul enfant ; lire le mot de gauche à droite = remonter l'arbre.

> **Mini-exemple déroulé.** Prenons le petit arbre `suffixes(suffix(s), nil)`. On
> remonte des feuilles vers le sommet :
> 1. `suffix(s)` est une feuille → on applique `suffix() → q_suf`, état **q_suf** ;
> 2. `nil` est une feuille → `nil() → q_nil`, état **q_nil** ;
> 3. le nœud `suffixes` a pour enfants les états `(q_suf, q_nil)` → la règle
>    `suffixes(q_suf, q_nil) → q_sufs` s'applique, état **q_sufs**.
> On a « plié » l'arbre du bas vers le haut, exactement comme un AFD consomme un mot
> symbole par symbole. C'est tout le principe ; le reste n'est que la liste des règles.

### 2.2 L'automate de ce TP

Le fichier `tree_automaton.hpp` réalise l'automate suivant. Alphabet rangé :

```
Σ = { word⁽²⁾, rest⁽²⁾, prefixes⁽²⁾, suffixes⁽²⁾,        (internes, arité 2)
      prefix⁽⁰⁾, root⁽⁰⁾, suffix⁽⁰⁾, nil⁽⁰⁾ }            (feuilles, arité 0)
```

États `Q = { q_pre, q_root, q_suf, q_nil, q_sufs, q_prefs, q_rest, q_word }`,
finaux `Q_f = { q_word }`, et `Δ` :

```
prefix() → q_pre     root() → q_root     suffix() → q_suf     nil() → q_nil

suffixes(q_suf, q_sufs) → q_sufs        suffixes(q_suf, q_nil) → q_sufs
prefixes(q_pre, q_prefs) → q_prefs      prefixes(q_pre, q_nil) → q_prefs
rest(q_root, q_sufs) → q_rest           rest(q_root, q_nil) → q_rest
word(q_prefs, q_rest) → q_word          word(q_nil, q_rest) → q_word
```

**En clair**, ces règles encodent une définition récursive : une *chaîne de suffixes*
est « un suffixe, puis une chaîne de suffixes (ou rien) » ; un *reste* est « une racine,
puis ses suffixes » ; un *mot* est « d'éventuels préfixes, puis un reste ». Le **seul**
état final `q_word` n'est atteignable que par un arbre respectant ce gabarit — c'est
ainsi que l'automate **valide** la bonne formation. (Comparez : c'est la version
« arbres » d'une grammaire régulière ; cf. Bonus B2 et TATA [1].)

> **Exercice 2.2.** Déroulez l'exécution ascendante sur l'arbre de `a-na-pend-a` :
> `word( prefixes(prefix(a), prefixes(prefix(na), nil)), rest(root(pend), suffixes(suffix(a), nil)) )`.
> Annotez chaque nœud par son état, dans l'ordre, et concluez accept/reject.

> **Exercice 2.3 (rejets).** Pour chacun, dites quel nœud **bloque** (aucune règle
> applicable) :
> (a) `word(nil, rest(suffix(er), nil))` ; (b) `word(nil, rest(root(a), suffixes(root(b), nil)))` ;
> (c) `rest(root(a), nil)` pris comme racine de l'arbre (sans `word`).

### 2.3 Langage, déterminisme, complexité, frontière

> **Exercice 2.4.** (a) Décrivez en français le langage d'arbres `L(A)`. (b) Montrez
> que `A` est **déterministe ascendant** (pour tout `(f, q₁…qₙ)`, au plus une règle) —
> conséquence sur l'unicité de l'exécution ? (c) Montrez que la reconnaissance est en
> **O(n)** (`n` = nombre de nœuds).

> **Exercice 2.5 (le pont).** La **frontière** d'un arbre accepté est un mot `p* r s*`.
> Montrez que `{ yield(t) | t ∈ L(A) }` est **exactement** le langage régulier de
> l'Exercice 1.1. *Vous reliez l'automate d'arbres (structure) à l'automate fini (surface).*

---

## 3. Implémentation et extension (≈ 1 h 15)

On utilise `tree_automaton.hpp` : constructeurs `word / rest / prefixes / suffixes /
prefix / root / suffix / nil`, classe `TreeAutomaton` (`run`, `accepts`, `add_rule`,
`add_final`), fonction `classify` (→ `BARE / SUFFIXED / PREFIXED / CIRCUMFIXED`).

> **Exercice 3.1.** Compilez et lancez `ta_check` (`make ta_check`). Confirmez votre
> trace de l'Exercice 2.2. **Ajoutez** les trois arbres mal formés de l'Exercice 2.3
> et vérifiez qu'ils sont **rejetés**.

> **Exercice 3.2.** Dans `TreeAutomaton::run`, expliquez en 3–4 lignes l'algorithme.
> `Δ` est ici une **table** indexée par `(Kind, états des enfants)` : quel est le coût
> d'une transition ? Comparez à une recherche linéaire dans une liste de règles.

> **Exercice 3.3.** Donnez un mot pour **chacune** des 4 classes (`BARE`, `SUFFIXED`,
> `PREFIXED`, `CIRCUMFIXED`), construisez l'arbre, vérifiez la classe renvoyée par
> `classify`.

> **Exercice 3.4 (cœur du TP) — l'infixation.** Certaines langues insèrent un **infixe**
> *à l'intérieur* de la racine (p. ex. `sulat` → `s‹um›ulat`). L'alphabet Σ actuel ne
> peut pas le représenter.
> (a) Proposez une extension de Σ (nouveau(x) symbole(s) rangé(s), p. ex.
>     `infixed⁽³⁾(root_left, infix, root_right)`) et les règles `Δ` associées.
> (b) Réalisez-la : dérivez/instanciez un `TreeAutomaton`, ajoutez états et règles via
>     `add_rule`/`add_final`, et reconnaissez `s‹um›ulat`.
> (c) **Théorie.** La **réduplication** (copie d'une partie de la racine) engendre-t-elle
>     un langage d'arbres **régulier** ? Intuition (lien avec `{ww}`, non régulier sur
>     les mots) et conséquence pour un automate d'arbres *à états finis*. *(Indice
>     linguistique réel : Culy 1985 [13] montre que la réduplication du bambara sort
>     même du hors-contexte.)*

---

## 4. Application : surface → arbre → automate (≈ 45 min)

`morph_demo.cpp` réalise la chaîne complète, **sans aucune annotation** :
1. **découverte** de morceaux d'affixes par une heuristique **classique** d'alternance
   (un affixe alterne avec ∅ : `X` et `X+suf` — resp. `pre+X` — tous deux attestés ;
   idée de Z. Harris, 1955 [11] ; voir aussi Goldsmith 2001 [12]) ;
2. **segmentation** gloutonne de chaque mot en `(préfixes*, racine, suffixes*)` ;
3. **construction de l'arbre**, puis **validation + classification** par l'automate.

Deux mini-corpus synthétiques (générés par `gen_corpora.py`, vérité-terrain connue) :
`corpus_A_prefixing.txt` (affixes en tête) et `corpus_B_suffixing.txt` (affixes en queue).

> **Exercice 4.1.** Lancez `./morph_demo corpus_A_prefixing.txt corpus_B_suffixing.txt`.
> Pour chaque corpus, relevez les affixes découverts et la **répartition des classes**
> renvoyée par l'automate. Comparez les affixes découverts à la **vérité-terrain**
> imprimée par `gen_corpora.py`. La répartition des classes distingue-t-elle A de B ?

> **Exercice 4.2.** Modifiez `gen_corpora.py` pour produire une **3ᵉ langue** dont les
> mots portent **à la fois** un préfixe et un suffixe. Que doit renvoyer `classify` ?
> Vérifiez.

> **Exercice 4.3 (discussion).** L'automate `tree_automaton.hpp` est **le même** quelle
> que soit la langue (mêmes `Q, Σ, Δ`) ; seuls changent les affixes injectés. Quel est
> l'intérêt — et la **limite** — d'un reconnaisseur de structure indépendant du
> vocabulaire ? (Reliez à l'infixation de l'Exercice 3.4.)

---

## 5. Mini-projet (bonus, au choix)

- **B1. Minimisation.** Implémentez la minimisation d'un automate d'arbres (fusion des
  états équivalents). L'automate de ce TP est-il minimal ?
- **B2. Grammaire d'arbres régulière ⇄ automate.** Donnez la grammaire d'arbres
  régulière engendrant `L(A)` et prouvez l'équivalence grammaire ⇄ automate.
- **B3. Partage de structure.** Représentez les arbres en **DAG** (sous-arbres
  identiques partagés, *hash-consing*) ; mesurez le taux de compression sur 10 000 mots.
- **B4. Unicode.** `morph_demo` segmente en octets (ASCII). Réécrivez la segmentation
  par **points de code** UTF-8 et testez sur une langue à diacritiques.

---

## 6. Livrables et barème

**Archive** `nom1_nom2.zip` : (1) **rapport PDF** (théorie 1.1–1.2, 2.2–2.5, 4.3 ;
traces ; complexité) ; (2) **code** (3.1, 3.4, 4.2) ; (3) **tests** (≥ 8 cas, dont les
4 classes et ≥ 3 mal formés).

| Critère | Points |
|---|---:|
| **Théorie** (1.1–1.2, 2.2–2.5) — définitions, traces, *yield*, complexité | **6** |
| **Implémentation** (3.1–3.3) — exécution, lecture, classification | **4** |
| **Extension infixation** (3.4) — Σ/Δ corrects + reconnaissance + réflexion réduplication | **5** |
| **Application** (4.1–4.3) — mesure sur corpus + analyse | **3** |
| **Qualité** — tests, lisibilité, complexité argumentée | **2** |
| **Bonus** (un des B1–B4) | **+3** |
| **Total** | **/20 (+3)** |

---

## Annexe A — Carte de référence

`A = (Q, Σ, Q_f, Δ)`, `Q_f = {q_word}` ; voir §2.2. Exécution ascendante déterministe ;
acceptation ssi racine → `q_word` ; coût O(n).

## Annexe B — Squelette `ta_check.cpp`

```cpp
#include "tree_automaton.hpp"
#include <iostream>
using namespace ta;
int main() {
    TreeAutomaton A;
    auto t = word(prefixes(prefix("a"), prefixes(prefix("na"), nil())),
                  rest(root("pend"), suffixes(suffix("a"), nil())));   // a-na-pend-a
    std::cout << (A.accepts(t) ? "ACCEPT " : "REJECT ")
              << class_name(classify(A, t)) << "  yield=\"" << yield(t) << "\"\n";
    return 0;
}
// g++ -std=c++17 -O2 ta_check.cpp -o ta_check && ./ta_check
```

---

## Bibliographie

> Les références marquées **(libre)** sont disponibles gratuitement en ligne.

**Rappels — automates finis & langages formels**
- [A] M. Sipser, *Introduction to the Theory of Computation*, 3ᵉ éd., Cengage, 2012.
- [B] J. Hopcroft, R. Motwani, J. Ullman, *Introduction to Automata Theory, Languages, and Computation*, 3ᵉ éd., Pearson, 2006.

**Automates d'arbres — le cœur du TP**
- [1] H. Comon, M. Dauchet, R. Gilleron, C. Löding, F. Jacquemard, D. Lugiez, S. Tison,
  M. Tommasi, *Tree Automata Techniques and Applications (TATA)*, 2007. **(libre :
  `tata.gforge.inria.fr`)** — la référence de base, complète et gratuite.
- [2] F. Gécseg, M. Steinby, *Tree Automata*, Akadémiai Kiadó, 1984 ; réédition
  **(libre : arXiv:1509.06233, 2015)**.
- [3] J. W. Thatcher, J. B. Wright, « Generalized finite automata theory with an
  application to a decision problem of second-order logic », *Mathematical Systems
  Theory* 2(1):57–81, 1968. *(Article fondateur des automates d'arbres ascendants.)*
- [4] J. Doner, « Tree acceptors and some of their applications », *Journal of Computer
  and System Sciences* 4(5):406–451, 1970.

**Applications**
- [6] M. Murata, D. Lee, M. Mani, K. Kawaguchi, « Taxonomy of XML schema languages
  using formal language theory », *ACM Trans. on Internet Technology* 5(4):660–704, 2005.
  *(Les schémas XML sont des langages d'arbres réguliers.)*
- [7] A. V. Aho, M. Ganapathi, S. W. K. Tjiang, « Code generation using tree matching
  and dynamic programming », *ACM TOPLAS* 11(4):491–516, 1989. *(Sélection
  d'instructions par filtrage d'arbres — l'outil « twig ».)*
- [8] A. Bouajjani, P. Habermehl, A. Rogalewicz, T. Vojnar, « Abstract Regular Tree
  Model Checking », *ENTCS* 149(1):37–48, 2006. *(Vérification par automates d'arbres.)*

**Morphologie computationnelle — l'application du TP**
- [9] K. Koskenniemi, *Two-Level Morphology: A General Computational Model for
  Word-Form Recognition and Production*, Université d'Helsinki, 1983.
- [10] K. R. Beesley, L. Karttunen, *Finite State Morphology*, CSLI Publications, 2003.
- [11] Z. S. Harris, « From phoneme to morpheme », *Language* 31(2):190–222, 1955.
  *(Découverte d'affixes par alternance — l'heuristique de l'Exercice 4.)*
- [12] J. Goldsmith, « Unsupervised learning of the morphology of a natural language »,
  *Computational Linguistics* 27(2):153–198, 2001.

**Réduplication & limites (Exercice 3.4c)**
- [13] C. Culy, « The complexity of the vocabulary of Bambara », *Linguistics and
  Philosophy* 8:345–351, 1985. *(La réduplication peut dépasser le hors-contexte.)*
- [14] B. Roark, R. Sproat, *Computational Approaches to Morphology and Syntax*,
  Oxford University Press, 2007.
