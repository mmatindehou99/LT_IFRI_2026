<!-- Charte IUT/IFRI — bleu #1A3A6B / orange #E07B20 -->

# Jour 4 — Calculabilité : machine de Turing, MTU, calculatrice

**Module produit :** `formlang/turing.py`, `formlang/utm.py`
**Application :** `apps/calc/machines.py`, `apps/calc/calculator.py`
**Tests cibles :** `tests/test_turing.py`, `tests/test_calc.py`
**Barème du jour :** 4 pts (+1 bonus)

---

## Contexte — le sommet de la hiérarchie

Jusqu'ici, nos automates **reconnaissaient** des structures (un motif, une
imbrication, un arbre). Aujourd'hui on **calcule**. La machine de Turing ajoute
le seul ingrédient qui manquait : un **ruban réinscriptible et non borné**, à la
fois entrée, mémoire de travail et sortie. C'est ce qui fait passer du « décider
si » au « calculer quoi ».

Puis vient la bascule conceptuelle du cours : la **machine universelle** `U`.
Elle prend en entrée la **description d'une machine** `⟨M⟩` (une donnée !) plus un
mot `w`, et **se comporte comme `M` sur `w`**. Le programme devient une donnée :
c'est l'ancêtre de l'interpréteur et de l'ordinateur à programme enregistré.

Enfin, le revers : cette universalité a un **prix**. « `U` s'arrête-t-elle sur
`⟨M⟩##w` ? » est **indécidable**. On gagne tout le calculable, on perd la
décidabilité.

> **Statut de vérification.** Les tables `ADD` et `SUB` fournies ont été
> **tracées à la main** ; `MUL`/`DIV` sont obtenues par **composition** de ces
> machines primitives. La garantie finale reste `pytest`.

---

## Conventions

Entier `n` en **unaire** : `n ↦ 1ⁿ` (donc `0` = mot vide). Opérandes séparées par
`+ - * /`. Blanc = `_`. La fonction de transition d'une MT :
`δ : (q, a) → (q', b, d)` avec `d ∈ {L, R, S}`.

---

## A. Théorie (à rédiger) — 2 pts

**Q4.1 — Encodage `⟨M⟩` (0,5 pt).**
Décrire un schéma d'encodage **injectif et décodable** d'une MT `M` (numérotation
des états et symboles, linéarisation de `δ` en liste de quintuplets). Expliquer
pourquoi l'injectivité et la décodabilité sont indispensables à `U`.
*(Dans le code, `utm.encode` / `utm.decode` jouent ce rôle via JSON.)*

**Q4.2 — Principe de la MTU (0,5 pt).**
Énoncer l'invariant `U(⟨M⟩ ## w) “=” M(w)` et décrire **un cycle de simulation**
(lire le symbole simulé → chercher la transition dans `⟨M⟩` → écrire → déplacer →
mettre à jour l'état). Que doit maintenir `U` sur son ruban à tout instant ?

**Q4.3 — Surcoût de simulation (0,5 pt) — à *sourcer*.**
Discuter le surcoût en temps de la simulation universelle. Mentionner : une MTU
**multi-ruban** simule `t` étapes en `O(t · |⟨M⟩|)` ; le passage multi-ruban →
mono-ruban coûte au plus un facteur **quadratique** ; résultat classique
(Hennie–Stearns) : un ralentissement seulement **logarithmique** est atteignable.
**Citer la source ; ne donner aucune constante « de mémoire ».**

**Q4.4 — Indécidabilité de l'arrêt (0,5 pt).**
Montrer, par **diagonalisation**, que le problème « `M` s'arrête sur `w` »
(HALT) est **indécidable**. Conclure : `U` peut simuler des machines qui ne
s'arrêtent jamais ; l'universalité **n'implique pas** l'omniscience.

---

## B. Pratique — 2 pts

**E4.1 — MT générique (`formlang/turing.py`) (0,5 pt).**
Vérifier/compléter `TuringMachine.run` : ruban `dict` **bi-infini**, arrêt sur
état acceptant **ou** transition manquante, garde `max_steps` (boucle infinie
suspectée → exception), **trace** disponible (`trace=True`).

**E4.2 — Machine universelle (`formlang/utm.py`) (0,5 pt).**
Implémenter `encode`/`decode` et `UniversalTM.run(⟨M⟩, w)`. Vérifier
l'invariant : pour `M = ADD`, `U(⟨M⟩, w)` produit **le même ruban** et **le même
verdict** que `M.run(w)` (test `test_utm_simule_comme_la_machine`), et le
**round-trip** `decode(encode(M))` recalcule correctement (`test_round_trip`).

**E4.3 — Calculatrice (`apps/calc/`) (1 pt).**
`Calculatrice` : `+` et `-` via les **vraies MT** `ADD`/`SUB` ; `*` et `/` par
**composition** (addition / soustraction répétées) ; `chainer(...)` pour
enchaîner. Faire passer le test **exhaustif** sur `0 ≤ n, m ≤ 6` (les quatre
opérations) et le chaînage `(((2+1)*2)-1)//2 = 2`.

---

## C. Explication des tables de transition (le cœur du jour) — inclus

> Compétence évaluée à l'oral et au rapport : **lire et justifier une table `δ`
> ligne par ligne**, en reliant chaque ligne à une intention et à un invariant.
> Grille : *où suis-je* (état = phase + mémoire finie) · *que vois-je* (symbole) ·
> *que fais-je* (écris, bouge) · *où vais-je* (état suivant). **L'état encode la
> mémoire finie ; le ruban encode la mémoire illimitée.**

### Table ADD — `1ⁿ + 1ᵐ → 1ⁿ⁺ᵐ`
(a) (q0,1) → (q0,1,R)    q0 : je parcours n ; rien n'est modifié
(b) (q0,+) → (q1,1,R)    ASTUCE : le '+' devient '1' -> les deux blocs sont collés (1^{n+1+m})
(c) (q1,1) → (q1,1,R)    q1 : je parcours m vers la fin
(d) (q1,) → (q2,,L)    fin du mot : demi-tour pour corriger le +1 introduit en (b)
(e) (q2,1) → (qf,_,S)    j'efface UN '1' (compense le '+'), puis j'accepte

**Invariant :** après (b), le ruban contient `n+1+m` symboles « 1 » ; on en
retire exactement un ⇒ `n+m`. Coût `O(n+m)`.

**Trace `2+1` :** `11+1` → (b) écrit 1 → `1111` → q1 va au blanc → q2 efface le
dernier → **`111` = 3**. ✔

### Table SUB — `1ⁿ - 1ᵐ → 1ⁿ⁻ᵐ` (hypothèse `n ≥ m`)

q0 : aller au '-'            (q0,1)→(q0,1,R)  (q0,X)→(q0,X,R)  (q0,-)→(q1,-,R)
q1 : prendre un '1' de m     (q1,1)→(q2,X,L)  (q1,X)→(q1,X,R)  (q1,)→(q4,,L)  ← m épuisé
q2 : revenir vers le '-'     (q2,X)→(q2,X,L)  (q2,-)→(q3,-,L)
q3 : barrer un '1' de n      (q3,1)→(q0,X,R)  (q3,X)→(q3,X,L)
q4 : nettoyage final         (q4,X)→(q4,,L)  (q4,-)→(q4,,L)  (q4,1)→(q4,1,L)  (q4,)→(qf,,S)
**Idées clés à expliquer dans le rapport (souvent ratées) :**
- `(q0,X)→R` et `(q1,X)→R` : **sans ces lignes, la machine se bloque au 2ᵉ tour**
  car elle re-rencontre ses propres marques `X`. *Une table doit gérer ses
  propres traces.*
- On barre `n` **de droite à gauche** (`q3`) : les `1` survivants restent
  **contigus à gauche** ⇒ sortie propre, sans étape de compactage.
- La fin de `m` est détectée par un **blanc** (`q1,_`), pas par un compteur : un
  automate fini ne compte pas — **c'est le ruban qui compte**.

Coût `O(n·m)`.

### MUL / DIV — par composition (macro-machines)

`*` = additions répétées (`m` appels **réels** à `ADD`) ; `/` = soustractions
répétées (compteur de quotient + reste). **Composer des MT est légitime** :
c'est exactement ce que fait une MTU qui orchestre des sous-machines. *(Une table
**monolithique** unique pour `*` est laissée en bonus, §E4.4.)*

---

## Sorties console attendues (référence)

```text
$ pytest -q tests/test_turing.py tests/test_calc.py
.......                                                         [100%]
7 passed
```

```python
>>> from apps.calc.calculator import Calculatrice
>>> c = Calculatrice()
>>> c.addition(3, 2), c.soustraction(4, 2), c.multiplication(3, 2), c.division(7, 3)
(5, 2, 6, (2, 1))
>>> c.chainer(2, [("+",1), ("*",2), ("-",1), ("/",2)])
2
```

---

## Mini-barème du jour (4 pts + 1 bonus)

| Item | Détail | Pts |
|---|---|---:|
| Q4.1 | encodage `⟨M⟩` injectif/décodable | 0,5 |
| Q4.2 | principe MTU + cycle de simulation | 0,5 |
| Q4.3 | surcoût **sourcé** (pas de constante inventée) | 0,5 |
| Q4.4 | indécidabilité de l'arrêt (diagonalisation) | 0,5 |
| E4.1 | MT générique (ruban, arrêt, trace) | 0,5 |
| E4.2 | MTU + invariant `U(⟨M⟩,w)=M(w)` | 0,5 |
| E4.3 | calculatrice (tests exhaustifs + chaînage) | 1 |
| **Bonus** | table **monolithique** de `MUL` validée par le simulateur | +1 |

> *Gate :* `apps/calc` ne doit pas réécrire une boucle d'exécution de MT — il
> **décrit des tables** et les fait tourner via `formlang.turing` /
> `formlang.utm`. *Honnêteté :* le surcoût de simulation doit être **référencé**.

---

## Références

- M. Sipser, *Introduction to the Theory of Computation* — machine universelle,
  encodage, indécidabilité de l'arrêt, réductions. *(À consulter pour Q4.3/Q4.4
  avant de citer une borne.)*
- Hennie & Stearns (simulation multi-ruban, ralentissement logarithmique) — pour
  Q4.3 : citer la source, ne pas donner de constante de mémoire.
- Hopcroft, Motwani, Ullman — pont machines / langages récursivement
  énumérables.

*Fin du jour 4 → passez à `jour5_integration.md`.*
