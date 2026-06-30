<!-- Charte IUT/IFRI — bleu #1A3A6B / orange #E07B20 -->

# Jour 2 — Étage hors-contexte : grammaires & automate à pile

**Module produit :** `formlang/pda.py`, `formlang/cfg.py`
**Application :** `apps/shield/delimiters.py`
**Tests cibles :** `tests/test_regular.py` (PDA), `tests/test_cfg_nerode.py` (CFG)
**Barème du jour :** 4 pts (+1 bonus)

> ⚠️ **Cadre éthique.** Toujours structurel : alphabet
> `Σ₃ = {a, o, r, [, ], (, )}`. Aucun contenu réel.

---

## Contexte — quand le régulier ne suffit plus

Hier, une mémoire bornée suffisait. Aujourd'hui, on attaque les **faux
délimiteurs** : un *prompt* imite un bloc « système » `[ … ]` ou un cadre
« fictionnel » `( … )`, éventuellement **imbriqués**. Vérifier que tout est
**bien ouvert/fermé et correctement imbriqué** revient à reconnaître un langage
de type **Dyck** — c'est **hors-contexte**, donc **hors de portée** d'un automate
fini.

La nouveauté, c'est la **pile** : une mémoire potentiellement **non bornée**, mais
disciplinée (dernier entré, premier sorti). C'est exactement ce qu'il faut pour
compter une profondeur d'imbrication arbitraire. Au jour 3, cette même
imbrication deviendra native dans un **arbre**.

---

## A. Théorie (à rédiger) — 2,5 pts

**Q2.1 — Non-régularité par le lemme de l'étoile (1,5 pt).**
Soit `D = { [ⁿ ]ⁿ | n ≥ 0 }` (blocs système purement imbriqués). Montrer, **par
le lemme de l'étoile** (*pumping lemma*) pour les langages réguliers, que `D`
**n'est pas régulier**. Conclure : le `SingularityDetector` (un AFD) **ne peut
pas** vérifier l'imbrication des délimiteurs.

> Squelette de preuve attendu : supposer `D` régulier de constante `p` ; prendre
> `w = [ᵖ]ᵖ` ; toute coupe `w = xyz` avec `|xy| ≤ p`, `|y| ≥ 1` force `y = [ᵏ`
> (`k ≥ 1`) ; alors `xy²z = [ᵖ⁺ᵏ]ᵖ ∉ D` → contradiction.

**Q2.2 — Grammaire hors-contexte (0,5 pt).**
Donner une grammaire `G` engendrant l'ensemble des *prompts* **bien
parenthésés** sur `Σ₃`, les jetons `a, o, r` pouvant apparaître librement entre
les délimiteurs.

> Forme attendue :
> ```
> S → S S | [ S ] | ( S ) | a | o | r | ε
> ```

**Q2.3 — Ambiguïté (0,5 pt).**
`G` est-elle **ambiguë** ? Si oui, exhiber **deux arbres de dérivation** pour un
même mot (ex. `aaa`), puis proposer une grammaire **non ambiguë** équivalente
(par exemple en imposant l'associativité de la concaténation).

---

## B. Pratique — 1,5 pt

**E2.1 — Automate à pile (`apps/shield/delimiters.py`) (1 pt).**
Implémenter `well_parenthesized(w)` **avec une pile** (acceptation par **pile
vide**) en instanciant `formlang.pda.DelimiterPDA` : empiler sur `[` et `(`,
dépiler sur `]`/`)` **si et seulement si** le sommet correspond, ignorer
`a, o, r, e`. Faire passer :

```python
well_parenthesized("[a(r)]")  # True
well_parenthesized("[a(r]")   # False  (fermeture qui ne correspond pas)
well_parenthesized("([)]")    # False  (chevauchement)
well_parenthesized("aor")     # True   (aucun délimiteur)
```

Donner aussi, dans le rapport, la **fonction de transition** `δ` du PDA :
```
δ(q, [ , X)   = (q, #[ · X)     empiler témoin de '['
δ(q, ( , X)   = (q, #( · X)     empiler témoin de '('
δ(q, ] , #[)  = (q, ε)          dépiler si sommet = #[
δ(q, ) , #()  = (q, ε)          dépiler si sommet = #(
δ(q, a , X)   = (q, X)          a, o, r : pile inchangée
δ(q, ε , Z₀)  = (q, ε)          acceptation par pile vide
```

**E2.2 — Génération par la grammaire (`formlang/cfg.py`) (0,5 pt).**
Utiliser `balanced_cfg()` et `generate(max_len)` pour **énumérer** les mots
bien parenthésés de longueur ≤ 4, et vérifier (test fourni) que `""`, `"[]"`,
`"()"`, `"[a]"`, `"[[]]"` y sont, et que `"["`, `"(]"` n'y sont **pas**.

---

## C. Pont vers le jour 3 (0 pt, à méditer)

La pile « compte » la profondeur d'imbrication **pendant** une lecture
gauche-droite. Un **arbre** rend cette imbrication **explicite et permanente** :
`[ … ]` devient un nœud `sys(…)`, `( … )` un nœud `frame(…)`. Demain, on ne
**compte** plus la profondeur — on la **lit dans la structure**. C'est ce qui
permettra de décider « un `role` **à l'intérieur** d'un bloc système », ce qu'un
AFD ne sait pas faire.

---

## Sorties console attendues (référence)

```text
$ pytest -q tests/test_cfg_nerode.py::test_cfg_engendre_des_mots_equilibres
.                                                               [100%]
1 passed
```

```text
$ pytest -q tests/test_regular.py::test_delimiters_pda
.                                                               [100%]
1 passed
```

---

## Mini-barème du jour (4 pts + 1 bonus)

| Item | Détail | Pts |
|---|---|---:|
| Q2.1 | non-régularité de `{[ⁿ]ⁿ}` (pompage complet) | 1,5 |
| Q2.2 | grammaire des prompts bien parenthésés | 0,5 |
| Q2.3 | ambiguïté + désambiguïsation | 0,5 |
| E2.1 | PDA `well_parenthesized` + δ rédigée | 1 |
| E2.2 | génération bornée par la CFG | 0,5 |
| **Bonus** | reconnaissance générale par **CYK** (au lieu de la seule génération) | +1 |

> *Gate :* `delimiters.py` doit **instancier `formlang.pda.DelimiterPDA`**, pas
> reprogrammer une pile à la main dans l'app.

---

## Références

- Hopcroft, Motwani, Ullman, *Introduction to Automata Theory* — lemme de
  l'étoile (réguliers), grammaires hors-contexte, automates à pile, ambiguïté.
- Pour le langage de Dyck et l'équivalence PDA ↔ CFG : tout cours standard de
  théorie des langages.

*Fin du jour 2 → passez à `jour3_arbres.md` (le pivot du projet).*