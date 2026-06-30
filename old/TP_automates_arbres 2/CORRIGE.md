# CORRIGÉ — TP Automates d'arbres (usage enseignant)

> Ne pas distribuer aux étudiants. Sorties machine reproductibles via `make run`.

## Partie 1

**1.1 — Regex et AFD.** Mot bien formé = `p* r s*` (exactement une racine).
AFD minimal sur `{p, r, s}` : **2 états utiles** + 1 puits.

```
        p              s
      ┌────┐         ┌────┐
      ▼    │         ▼    │
   ▶ (q0) ─┘   ─r→   (q1)* ─┘
     q0 --s--> ⊥        q1 --p--> ⊥,  q1 --r--> ⊥
```
- `q0` (racine pas encore lue, **non final**) : `p→q0`, `r→q1`, `s→⊥`.
- `q1` (racine lue, **final**) : `s→q1`, `p→⊥`, `r→⊥`.
Minimalité : `q0` et `q1` sont distinguables (`q1` final, `q0` non) ; aucun autre état
n'est nécessaire. ⊥ = puits (mot mal formé : suffixe avant racine, deux racines, etc.).

**1.2 — La frontière ne détermine pas la structure.** Deux arbres de même *yield*
`a na pend a` :
- T₁ = `word(prefixes(a, prefixes(na, nil)), rest(root(pend), suffixes(a, nil)))`
  (`pend` = racine, `a`/`na` préfixes, `a` suffixe) ;
- T₂ = `word(prefixes(a, prefixes(na, prefixes(pend, nil))), rest(root(a), nil))`
  (`a` final = racine, tout le reste préfixes).
Même frontière, **structures différentes** ⇒ la suite des feuilles (ce que lit un
automate fini) ne fixe pas l'analyse. Seul un objet qui contraint la **hiérarchie**
(grammaire / automate d'**arbres**) tranche.

## Partie 2

**2.2 — Trace ascendante de `a-na-pend-a`** (ordre post-fixe) :

| nœud | règle appliquée | état |
|---|---|---|
| `prefix(a)` | `prefix() → q_pre` | q_pre |
| `prefix(na)` | `prefix() → q_pre` | q_pre |
| `nil` (fin chaîne préf.) | `nil() → q_nil` | q_nil |
| `prefixes(na, nil)` | `prefixes(q_pre,q_nil) → q_prefs` | q_prefs |
| `prefixes(a, …)` | `prefixes(q_pre,q_prefs) → q_prefs` | q_prefs |
| `root(pend)` | `root() → q_root` | q_root |
| `suffix(a)` | `suffix() → q_suf` | q_suf |
| `nil` (fin chaîne suf.) | `nil() → q_nil` | q_nil |
| `suffixes(a, nil)` | `suffixes(q_suf,q_nil) → q_sufs` | q_sufs |
| `rest(pend, …)` | `rest(q_root,q_sufs) → q_rest` | q_rest |
| `word(…, …)` | `word(q_prefs,q_rest) → q_word` | **q_word** |

Racine → `q_word ∈ Q_f` ⇒ **ACCEPTÉ**.

**2.3 — Rejets** (le 1ᵉʳ nœud sans règle applicable) :
- (a) `rest(suffix(er)→q_suf, nil→q_nil)` : aucune règle `rest(q_suf, …)` (le 1ᵉʳ
  enfant de `rest` doit être `q_root`) ⇒ **REJECT** au nœud `rest`.
- (b) `suffixes(root(b)→q_root, nil→q_nil)` : aucune règle `suffixes(q_root, …)` (il
  faut `q_suf`) ⇒ **REJECT** au nœud `suffixes`.
- (c) `rest(root(a), nil) → q_rest`, mais `q_rest ∉ Q_f` ⇒ **REJECT** (racine de
  l'arbre non finale ; seul `q_word` est acceptant).

**2.4.** (a) `L(A)` = arbres `word(P, rest(root, S))` avec **exactement une** racine,
`P` ∈ {`nil`, chaîne de préfixes terminée par `nil`}, `S` ∈ {`nil`, chaîne de suffixes
terminée par `nil`}. (b) **Déterminisme** : `Δ` est une table indexée par
`(symbole, états des enfants)` ; chaque clé a **au plus une** image ⇒ à chaque nœud,
au plus une règle s'applique ⇒ exécution **unique**. (c) **O(n)** : `run` visite chaque
nœud une fois ; par nœud, collecte des états enfants (arité bornée) + **une** recherche
dans `Δ` (O(log|Δ|), |Δ| constant) ⇒ total O(n).

**2.5 — Frontière.** Par induction, le *yield* d'un arbre accepté concatène, de gauche
à droite : les étiquettes des `prefix` (chaîne `P`), puis l'unique `root`, puis les
`suffix` (chaîne `S`) — soit un mot `p* r s*`. Réciproquement tout `p* r s*` admet un
tel arbre. Donc `{ yield(t) | t ∈ L(A) } = { p* r s* }`, le langage **régulier** de
1.1. (C'est le lien automate d'arbres ↔ automate fini : la frontière d'un langage
d'arbres régulier est ici régulière.)

## Partie 3

**3.1 — Sortie attendue de `ta_check`** :
```
ACCEPT  BARE        BARE livre            [yield="livre"]
ACCEPT  SUFFIXED    SUFFIXED jou-er       [yield="jouer"]
ACCEPT  PREFIXED    PREFIXED na-penda     [yield="napenda"]
ACCEPT  CIRCUMFIXED CIRCUMFIXED a-na-pend-a [yield="anapenda"]
REJECT  INVALID     MALFORMÉ rest(suffix,nil)  [yield="er"]
REJECT  —           MALFORMÉ suffixes(root,nil)
```

**3.2.** `run` est un parcours **post-ordre** : on calcule récursivement l'état de
chaque enfant, on rejette dès qu'un enfant est `REJECT`, puis on cherche
`Δ[(kind, états_enfants)]`. La table (`std::map`) donne la transition en **O(log|Δ|)** ;
une liste de règles parcourue linéairement coûterait **O(|Δ|)** par nœud.

**3.3.** `livre` → BARE ; `jou+er` → SUFFIXED ; `na+penda` → PREFIXED ;
`a+na+pend+a` → CIRCUMFIXED. (Vérifié par `ta_check`.)

**3.4 — Infixation.**
(a) Étendre Σ : feuille `infix⁽⁰⁾` et symbole `infixed⁽³⁾(root_g, infix, root_d)`
placé là où une racine est attendue. (b) Règles à ajouter :
```
infix() → q_inf
infixed(q_root, q_inf, q_root) → q_root     // l'infixe scinde la racine ; le résultat
                                            // « vaut » une racine pour rest(…)
```
Implémentation (éditer `tree_automaton.hpp` : ajouter `Infix, Infixed` à `enum Kind`) ;
les r* états `qRoot=2`, le nouvel `q_inf=9` :
```cpp
TreeAutomaton A;
A.add_rule(Kind::Infix,   {},        9);   // infix() → q_inf
A.add_rule(Kind::Infixed, {2, 9, 2}, 2);   // infixed(root, infix, root) → q_root
// s<um>ulat = word(nil, rest(infixed(root(s), infix(um), root(ulat)), nil))
auto inf = std::make_shared<Tree>(); inf->kind = Kind::Infixed;
inf->kids = { root("s"), leaf(Kind::Infix, "um"), root("ulat") };
auto t = word(nil(), rest(inf, nil()));
// VÉRIFIÉ : ACCEPT, yield "sumulat", classe BARE (l'infixe n'étant ni préfixe ni
// suffixe). Variante : ajouter une classe INFIXED si l'on veut la distinguer.
```
(`run` gère déjà l'arité 3 : il collecte les états des 3 enfants et cherche la règle.)
(c) **Réduplication.** Copier une partie **de longueur arbitraire** de la racine exige
de comparer deux sous-structures égales — analogue à `{ww}`, **non régulier** sur les
mots (et `{ww}` n'est même pas hors-contexte). Un automate d'arbres **à états finis** a
une mémoire bornée : il ne peut pas vérifier l'égalité de deux sous-arbres de taille non
bornée. ⇒ la réduplication **n'est pas** un langage d'arbres régulier ; il faut un
formalisme plus puissant (p. ex. faiblement contextuel).

## Partie 4

**4.1 — Sortie attendue de `morph_demo`** :
```
== corpus_A_prefixing.txt ==  (1350 formes)
  affixes découverts : 8 préfixe(s), 0 suffixe(s)
  classes (via l'automate) :  BARE=150  PREFIXED=1200  SUFFIXED=0  CIRCUMFIXED=0  INVALID=0

== corpus_B_suffixing.txt ==  (1350 formes)
  affixes découverts : 0 préfixe(s), 9 suffixe(s)
  classes (via l'automate) :  BARE=150  PREFIXED=0  SUFFIXED=1200  CIRCUMFIXED=0  INVALID=0
```
Lecture : **A** est reconnue **PRÉFIXANTE** (150 racines nues = BARE, 150×8 formes
préfixées = PREFIXED), **B** **SUFFIXANTE**. Les 8 préfixes de A sont **tous**
retrouvés ; en B, l'heuristique trouve **9** suffixes au lieu de 8 — le 9ᵉ est `-n`,
légitime : pour beaucoup de racines, `racine+de` et `racine+den` coexistent, donc `-n`
**alterne avec ∅** (`…de` → `…den`). Bon exemple de **sur-génération** d'une heuristique
de découverte (à discuter).

**4.2.** Une 3ᵉ langue avec préfixe **et** suffixe sur chaque mot ⇒ `classify` doit
renvoyer **CIRCUMFIXED**. (Générer `pre+racine+suf`, vérifier `CIRCUMFIXED=…`.)

**4.3.** Avantage : **un seul** validateur de structure, indépendant du lexique et de la
langue (mêmes `Q, Σ, Δ`) ; seuls changent les affixes injectés. Limite : il **présuppose
le gabarit** `préfixes* racine suffixes*` (morphologie concaténative). Il échoue sur
l'**infixation** (Ex. 3.4), la **réduplication**, et la morphologie **gabaritique**
(racines consonantiques + schèmes) — non concaténatives.

## Partie 5 (bonus) — éléments d'évaluation

- **B1.** Minimisation par raffinement de partition des états (équivalence de Myhill-
  Nerode transposée aux arbres). L'automate du TP est déjà essentiellement minimal (un
  état par catégorie atteignable et distinguable).
- **B2.** Grammaire d'arbres régulière : non-terminaux = états ; productions = règles
  `Δ` lues `q → f(q₁,…,qₙ)` ; axiome = état final. Équivalence par construction directe
  dans les deux sens.
- **B3.** DAG / *hash-consing* : interner les sous-arbres identiques (table de hachage
  structure→id). Sur des formes morphologiques répétitives, fort partage (les `nil`, les
  feuilles, les chaînes courtes). Mesurer `#nœuds_uniques / #nœuds_dépliés`.
- **B4.** Segmentation par points de code UTF-8 : itérer en sautant les octets de
  continuation `10xxxxxx` ; tester sur une langue à diacritiques.
