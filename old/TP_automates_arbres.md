# TP — Des automates finis aux **automates d'arbres**
## Reconnaissance morphologique par automate d'arbre ascendant

> **Cours** : Théorie des langages — Master 1 Génie Logiciel, IFRI
> **Pré-requis** : langages formels, expressions régulières, grammaires,
> automates finis (DFA/NFA), déterminisation, minimisation.
> **Durée conseillée** : 1 séance de 4 h (ou 2 × 2 h) + rendu.
> **Langage d'implémentation** : C++17 (un squelette autonome est fourni —
> aucune dépendance externe).

---

## 0. Pourquoi ce TP ?

Jusqu'ici, vos automates lisent des **mots** : une suite *linéaire* de
symboles, parcourue de gauche à droite. Un DFA accepte un langage de mots
`L ⊆ Σ*`.

Mais beaucoup d'objets ne sont **pas** linéaires : un arbre de dérivation
d'une grammaire, l'AST d'un compilateur, un document XML/JSON, ou —
ce qui nous intéresse ici — la **structure morphologique d'un mot** :

```
            re·structur·ation
                  WORD
                 /    \
          PREFIXES     REST
           /   \       /   \
      PREFIX  NIL   ROOT   SUFFIXES
       "re"        "structur"  /   \
                          SUFFIX   SUFFIXES
                          "ation"   /    \
                                  ...     NIL
```

Pour reconnaître **l'ensemble des arbres bien formés** (et pas seulement
des mots bien formés), il faut généraliser le DFA : c'est l'**automate
d'arbre**. L'analyse morphologique par méthodes à états finis est un domaine
classique du traitement des langues (Roche & Schabes 1997 ; Comon *et al.*
2007) : on y représente la décomposition d'un mot en préfixes / racine /
suffixes par un **arbre**, et on valide cette décomposition par un automate.

Ce TP vous fait :
1. **définir** formellement un automate d'arbre ascendant ;
2. **l'implémenter** et l'exécuter sur de vrais arbres morphologiques ;
3. **compacter** une forêt d'arbres en DAG par *hash-consing* — la technique
   classique des dictionnaires morphologiques à états finis (Daciuk *et al.*
   2000) ;
4. **mesurer** le gain de compression sur un petit vocabulaire ;
5. (bonus) explorer deux propriétés classiques : **clôture par intersection**
   et **minimisation**.

---

## 1. Rappel express — du mot à l'arbre

### 1.1 Automate fini sur les mots (ce que vous savez)

Un DFA est `A = (Q, Σ, δ, q₀, F)` avec `δ : Q × Σ → Q`. On accepte
`w = a₁a₂…aₙ` si `δ̂(q₀, w) ∈ F`.

**Observation clé.** Un mot est un arbre *dégénéré* : une **branche
unaire**. `a₁·a₂·…·aₙ·⊥` est l'arbre

```
a₁(a₂(a₃(…aₙ(⊥))))
```

où chaque symbole a **un** fils. Un automate de mots est donc un cas
particulier d'automate d'arbre où **tous les symboles sont d'arité 1**
(plus une feuille `⊥`). Lire un mot de gauche à droite = remonter cette
branche de la feuille vers la racine.

### 1.2 Alphabet **classé** (ranked alphabet)

Pour les arbres, chaque symbole `f` a une **arité** `arity(f) ∈ ℕ`.
On note `Σ = Σ₀ ∪ Σ₁ ∪ Σ₂ ∪ …` où `Σₖ` regroupe les symboles d'arité `k`.

- `Σ₀` = **feuilles** (constantes).
- `Σₖ` (k≥1) = **nœuds internes** à `k` fils.

Un **arbre** `t ∈ T(Σ)` est défini inductivement :
- si `a ∈ Σ₀` alors `a` est un arbre ;
- si `f ∈ Σₖ` et `t₁,…,tₖ` sont des arbres, alors `f(t₁,…,tₖ)` est un arbre.

### 1.3 Un alphabet classé pour la morphologie

On fixe l'alphabet classé suivant pour encoder la décomposition d'un mot
(préfixes\*, racine, suffixes\*) :

| Symbole `f`   | Arité | Rôle                                   |
|---------------|:-----:|----------------------------------------|
| `PREFIX`      | 0     | feuille : un préfixe (« re », « un »)  |
| `ROOT`        | 0     | feuille : la racine lexicale           |
| `SUFFIX`      | 0     | feuille : un suffixe (« ation »)       |
| `NIL`         | 0     | feuille : liste vide (fin de chaîne)   |
| `SUFFIXES`    | 2     | `suffixes(SUFFIX, SUFFIXES\|NIL)`      |
| `PREFIXES`    | 2     | `prefixes(PREFIX, PREFIXES\|NIL)`      |
| `REST`        | 2     | `rest(ROOT, SUFFIXES\|NIL)`            |
| `WORD`        | 2     | `word(PREFIXES\|NIL, REST)` ← racine   |

Les chaînes de préfixes et de suffixes sont encodées « à la liste chaînée »
(cons-cellules `PREFIXES` / `SUFFIXES` terminées par `NIL`), exactement comme
on code une liste par un arbre binaire.

> **Q1 (théorie, 2 pts).** Donnez `Σ₀` et `Σ₂` pour cet alphabet. Y a-t-il
> des symboles d'arité 1 ? Écrivez l'arbre complet du mot
> **« re·structur·ation »** (préfixe `re`, racine `structur`, suffixe
> `ation`) en notation fonctionnelle `f(t₁,…)`.

---

## 2. Automate d'arbre **ascendant** (Bottom-Up Tree Automaton)

### 2.1 Définition

Un **automate d'arbre ascendant déterministe** (BUTA) est
`A = (Q, Σ, F, Δ)` où :

- `Q` est un ensemble **fini** d'états ;
- `Σ` est un **alphabet classé** ;
- `F ⊆ Q` est l'ensemble des **états finaux (acceptants)** ;
- `Δ` est un ensemble de **règles de transition** de la forme

  ```
  f(q₁, q₂, …, qₖ) → q        avec f ∈ Σₖ,  q₁…qₖ, q ∈ Q
  ```

  Pour une **feuille** `a ∈ Σ₀`, la règle est `a() → q` (souvent notée
  `a → q`).

`A` est **déterministe** si, pour tout `(f, q₁…qₖ)`, il existe **au plus
une** règle de membre gauche `f(q₁,…,qₖ)`.

### 2.2 Exécution (la fonction `run`)

On étiquette l'arbre des **feuilles vers la racine** par une fonction
`run : T(Σ) → Q ∪ {⊥}` :

```
run(a)            = q                 si  (a → q) ∈ Δ            (a ∈ Σ₀)
run(f(t₁,…,tₖ))   = q                 si  run(tᵢ)=qᵢ ≠ ⊥ pour tout i
                                       et (f(q₁,…,qₖ) → q) ∈ Δ
run(…)            = ⊥ (REJECT)        sinon
```

L'arbre `t` est **accepté** ssi `run(t) ∈ F`. Le langage reconnu est

```
L(A) = { t ∈ T(Σ)  |  run(t) ∈ F }   ⊆ T(Σ)
```

C'est un **langage d'arbres régulier**.

> **Comparaison.** Pour un DFA, `δ̂` remonte une branche unaire ; ici `run`
> remonte un arbre **branchant**, en combinant les états des fils via `Δ`.
> Le DFA est le cas « tout en arité 1 ».

### 2.3 L'automate morphologique du TP

On reconnaît les décompositions morphologiques bien formées avec
l'automate suivant :

```
Q = { Q_PREFIX, Q_ROOT, Q_SUFFIX, Q_NIL,
      Q_SUFFIXES, Q_PREFIXES, Q_REST, Q_WORD }
F = { Q_WORD }

Feuilles (Σ₀) :
    PREFIX  → Q_PREFIX
    ROOT    → Q_ROOT
    SUFFIX  → Q_SUFFIX
    NIL     → Q_NIL

Nœuds binaires (Σ₂) :
    SUFFIXES(Q_SUFFIX,  Q_SUFFIXES) → Q_SUFFIXES
    SUFFIXES(Q_SUFFIX,  Q_NIL)      → Q_SUFFIXES
    PREFIXES(Q_PREFIX,  Q_PREFIXES) → Q_PREFIXES
    PREFIXES(Q_PREFIX,  Q_NIL)      → Q_PREFIXES
    REST(Q_ROOT,        Q_SUFFIXES) → Q_REST
    REST(Q_ROOT,        Q_NIL)      → Q_REST
    WORD(Q_PREFIXES,    Q_REST)     → Q_WORD       (avec préfixe)
    WORD(Q_NIL,         Q_REST)     → Q_WORD       (sans préfixe)
```

> **Q2 (déroulé, 3 pts).** Déroulez `run` **état par état** sur l'arbre de
> « re·structur·ation » de Q1. Donnez la valeur de `run` à **chaque** nœud
> et concluez : l'arbre est-il accepté ?
>
> **Q3 (langage, 2 pts).** Décrivez en français le langage d'arbres `L(A)`
> reconnu par cet automate. *(Indice : quelle forme générale `word(…)` doit
> avoir un arbre accepté ?)* Donnez **un** arbre sur `Σ` qui est **rejeté**
> et expliquez à quel nœud `run` renvoie `⊥`.
>
> **Q4 (déterminisme, 1 pt).** Cet automate est-il déterministe au sens du
> §2.1 ? Justifiez en inspectant les membres gauches des règles.

---

## 3. Partie pratique A — implémenter le reconnaisseur

Le squelette `tp_squelette.cpp` (fourni) contient la structure d'arbre,
le constructeur, et l'ossature du BUTA avec des `// TODO`. Compilez :

```bash
g++ -std=c++17 -O2 -o tp tp_squelette.cpp && ./tp
```

> **E1 (5 pts).** Complétez la méthode `State recognize(const TreePtr&)`
> (parcours **post-ordre** : fils d'abord, puis application de `Δ`) et
> `bool accepts(const TreePtr&)`. Faites passer les tests fournis
> (`accepts(...)`).
>
> **E2 (3 pts).** Ajoutez la règle qui manque pour accepter un mot
> **sans suffixe** (ex. « chien » = `word(NIL, rest(ROOT, NIL))`). Vérifiez
> que `re·structur·ation`, `chien`, et `un·happi·ness` sont acceptés.
>
> **E3 (3 pts).** Fabriquez un arbre **mal formé** (ex. un `SUFFIX` placé
> en position de racine d'un `REST`) et montrez par un test que `accepts`
> renvoie `false`. Indiquez le nœud exact où `run` casse.

---

## 4. Partie pratique B — compaction par **hash-consing**

### 4.1 Le problème

Dans un vocabulaire réel, des **sous-arbres identiques** se répètent
massivement : le suffixe `-ing` apparaît dans des milliers de mots, la
chaîne `suffixes(SUFFIX "s", NIL)` aussi. Stocker chaque mot comme un arbre
**plein** gaspille la mémoire.

### 4.2 La solution : *hash-consing*

On définit la **congruence structurelle** `≡` sur les sous-arbres :

```
f(t₁,…,tₖ) ≡ g(s₁,…,sₘ)   ⟺   f=g, k=m, et tᵢ ≡ sᵢ pour tout i
```

Le *hash-consing* (Goto 1974 ; Filliâtre & Conchon 2006) consiste à fusionner
les sous-arbres **structurellement identiques** et à leur donner le **même
identifiant** (`NodeId`). On passe d'une **forêt d'arbres** à un **DAG**
(graphe orienté acyclique) où chaque sous-arbre distinct n'existe **qu'une
fois**. C'est le principe des **dictionnaires morphologiques minimaux** à
états finis (Daciuk *et al.* 2000). L'opération centrale est `intern` :

```cpp
NodeId intern(const TreePtr& t) {
    // 1. interner récursivement les enfants  → ids
    // 2. clé canonique = (type, label, ids_enfants)
    // 3. si clé déjà vue → renvoyer l'id existant   (fusion)
    //    sinon          → créer un nouvel id
}
```

> **E4 (6 pts).** Complétez `CompactStore::intern` (table de hachage
> `(type,label,enfants) → NodeId`). Sur le lot de mots fourni
> (`sample_vocab`), affichez :
> - le nombre total de nœuds **avant** partage (`total_nodes`),
> - le nombre de nœuds **uniques après** partage (`unique_nodes`),
> - le **taux de compression** `1 − unique/total`.
>
> **E5 (2 pts).** Donnez deux mots du lot qui **partagent** un sous-arbre
> après interning, et l'identifiant commun. Vérifiez que `get(intern(t))`
> reconstruit un arbre `≡ t` (round-trip **exact**).

> **Q5 (analyse, 2 pts).** Le taux de compression dépend de la
> **redondance** du vocabulaire. Pour quelle famille de langues (parmi :
> anglais isolant vs. **turc/finnois/coréen** agglutinants) attend-on le
> **plus** de partage de sous-arbres suffixaux ? Justifiez.

---

## 5. Partie bonus — propriétés classiques des langages d'arbres réguliers

Les langages d'arbres réguliers jouissent des mêmes bonnes propriétés que
les langages réguliers de mots (Comon *et al.* 2007, ch. 1).

> **E6 (bonus, 5 pts) — clôture par intersection.** Soient deux automates
> d'arbres `A₁` et `A₂` sur le même alphabet `Σ`. Construisez l'**automate
> produit** `A₁ × A₂` dont les états sont les couples `(q, q′)`, avec la
> règle
> `f((q₁,q₁′),…,(qₖ,qₖ′)) → (q, q′)`
> ssi `f(q₁,…,qₖ)→q ∈ Δ₁` **et** `f(q₁′,…,qₖ′)→q′ ∈ Δ₂`, et finaux
> `F₁ × F₂`. Implémentez-le et vérifiez que `L(A₁×A₂) = L(A₁) ∩ L(A₂)` sur
> trois arbres test.
>
> **Q6 (bonus, 4 pts) — minimisation.** Énoncez le résultat : tout langage
> d'arbres régulier admet un **automate déterministe minimal unique**,
> obtenu en **quotientant** les états par la congruence de Myhill–Nerode
> pour les arbres. Décrivez l'analogie **point par point** avec la
> minimisation d'un DFA que vous connaissez (états indistinguables →
> fusion). *(On ne demande pas l'implémentation, seulement l'énoncé et
> l'analogie.)*

---

## 6. Barème (sur 20, +9 bonus)

| Item | Pts |
|---|---:|
| **Théorie** Q1 (alphabet classé + arbre) | 2 |
| Q2 (déroulé `run`) | 3 |
| Q3 (langage `L(A)` + arbre rejeté) | 2 |
| Q4 (déterminisme) | 1 |
| **Pratique A** E1 (`recognize`/`accepts`) | 5 |
| E2 (règle « sans suffixe ») | 3 |
| E3 (arbre rejeté, point de cassure) | 3 |
| **Pratique B** E4 (hash-consing) | 6 |
| E5 (partage + round-trip) | 2 |
| Q5 (analyse compression) | 2 |
| **Bonus** E6 (produit / intersection) + Q6 (minimisation) | +9 |

> Normalisation : Théorie (8) + Pratique A (11) = 19 → ramené sur 12.
> Pratique B (10) → ramené sur 8. Total **/20**. Bonus en sus.

---

## 7. Modalités de rendu

- **Archive** `NOM_Prenom_TP_arbres.zip` : `tp_squelette.cpp` complété +
  un `REPONSES.md` (réponses Q1–Q6) + sortie console (`./tp > out.txt`).
- Code qui **compile** (`g++ -std=c++17`) et **tests qui passent**.
- Tout sous-arbre identique doit être fusionné **une seule fois** (E4) :
  un `intern` qui ne partage rien = 0 sur E4.
- **Reportez les vrais chiffres** de votre sortie, même si la compression
  est faible sur le petit lot : on note la rigueur de la mesure, pas le
  chiffre.

---

## 8. Pour aller plus loin (références)

- H. Comon *et al.*, **TATA — Tree Automata Techniques and Applications**
  (2007), ch. 1 (automates ascendants, déterminisation, clôtures) et
  minimisation. *La* référence libre et complète.
- F. Gécseg, M. Steinby, **Tree Automata** (1984 ; rééd. 2015).
- E. Roche, Y. Schabes (dir.), **Finite-State Language Processing**
  (MIT Press, 1997) — morphologie à états finis.
- J. Daciuk, S. Mihov, B. Watson, R. Watson, *Incremental construction of
  minimal acyclic finite-state automata*, **Computational Linguistics** 26(1),
  2000 — dictionnaires morphologiques minimaux (le pendant « mots » du DAG).
- J.-C. Filliâtre, S. Conchon, *Type-safe modular hash-consing*, **ML
  Workshop**, 2006 — le hash-consing, propre et moderne.
- J. Hopcroft, J. Ullman, **Introduction to Automata Theory** (1979), ch. 3
  — pour le pont DFA → arbre et la minimisation de DFA.

---

*TP conçu pour le cours de Théorie des langages, Master GL — IFRI.
Toute notion théorique correspond à un résultat classique référencé et à du
code exécutable fourni.*
