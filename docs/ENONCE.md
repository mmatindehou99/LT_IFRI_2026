<!-- Charte IUT/IFRI — bleu #1A3A6B / orange #E07B20 -->

# Projet intégrateur — De l'automate fini à la machine universelle

**Établissement :** IUT / IFRI — Master Génie Logiciel
**Module :** Théorie des langages & calculabilité
**Auteur du sujet :** Dr. Mêton ATINDEHOU
**Durée :** 1 semaine (5 jours + soutenance) · **Binôme** · **Langage :** Python 3.10+
**Bibliothèque à construire :** `formlang`

> Ce document est le **chapeau** du projet. Il pose le cadre commun à toutes les
> journées. Les énoncés détaillés, question par question, sont dans les cinq
> fiches `jour1_regulier.md` … `jour5_integration.md`. Le corrigé
> (`CORRIGE.md`) est **réservé à l'enseignant**.

---

## 1. De quoi parle ce projet ?

Pendant tout votre cursus, vos automates ont lu des **mots** : une suite
linéaire de symboles, parcourue de gauche à droite. Mais une question revient à
chaque étage de la théorie des langages, toujours la même, de plus en plus
difficile : **« comment reconnaître une structure ? »**

- Reconnaître qu'un mot contient un motif → **automate fini** (régulier).
- Reconnaître que des délimiteurs sont bien imbriqués → **automate à pile**
  (hors-contexte).
- Reconnaître qu'une configuration dangereuse apparaît dans un **arbre** →
  **automate d'arbres**.
- Reconnaître… *n'importe quel calcul* → **machine de Turing**, et finalement
  **machine universelle**.

Ce projet vous fait **construire vous-même** chacun de ces reconnaisseurs, dans
**une seule bibliothèque en couches** (`formlang`), puis les **réutiliser** dans
des applications concrètes. La leçon, répétée à chaque étage :

> **Plus la structure à reconnaître est riche, plus il faut de mémoire — et il
> existe un seuil (la machine universelle) au-delà duquel on gagne
> l'universalité mais on perd la décidabilité.**

---

## 2. Le fil rouge : monter la hiérarchie de Chomsky

| Jour | Étage | Pouvoir d'expression | Ce que vous construisez |
|---|---|---|---|
| 1 | Régulier | langages réguliers | AFD, AFN, transducteur fini |
| 2 | Hors-contexte | langages algébriques | grammaire, automate à pile |
| 3 | **Arbres** | langages d'arbres réguliers | **automate d'arbres ascendant** |
| 4 | Calculable | récursivement énumérable | machine de Turing, **machine universelle** |
| 5 | Transversal | — | minimisation, congruence, intégration |

Chaque étage **contient** le précédent : un mot est un arbre dégénéré (une
branche unaire) ; un automate fini est un automate d'arbres où tous les symboles
sont d'arité 1. Vous le **vérifierez en code**.

---

## 3. Une bibliothèque, deux études de cas

Principe de conception **noté** : les applications n'ont **pas le droit** de
réécrire un automate. Elles **instancient** ceux de `formlang`. C'est ce qui
fait l'unité du projet (et non « trois TP côte à côte »).

apps/morpho ─┐
apps/shield ─┼─► formlang.tree      (le MÊME automate d'arbres pour les deux !)
apps/shield ─┼─► formlang.dfa / fst / pda
apps/calc   ─┴─► formlang.turing ─► formlang.utm
pipeline.py ───► (toutes les apps)

- **Étude de cas A — Morphologie.** De la surface d'un mot à son **arbre**
  (préfixes\* racine suffixes\*), validé puis classé (BARE / PREFIXED /
  SUFFIXED / CIRCUMFIXED) par un automate d'arbres.
- **Étude de cas B — Shield (défense structurelle).** Un détecteur qui décide si
  un *prompt* doit être **bloqué**, en montant la même hiérarchie : motif (AFD),
  normalisation (FST), délimiteurs (PDA), **configuration dangereuse dans
  l'arbre** (automate d'arbres).
- **Étude de cas C — Calculabilité.** Une calculatrice unaire dont les opérations
  sont de **vraies machines de Turing**, exécutées **par la machine
  universelle**.

---

## 4. Modèle abstrait commun (à lire avant tout)

### 4.1 Pour les volets « mots » (jours 1, 2, 5)

On travaille sur l'alphabet de jetons abstraits `Σ = {a, o, r, e}`, augmenté des
délimiteurs `[ ] ( )` aux jours 2–3 :

| Jeton | Symbole | Signification (bénigne) |
|---|---|---|
| `TXT`  | `a` | texte ordinaire, anodin |
| `OVR`  | `o` | marqueur d'**annulation** d'instruction |
| `ROLE` | `r` | marqueur de **réassignation de rôle** |
| `ENC`  | `e` | bloc **encodé / obfusqué** |
| `SYS[` `]SYS` | `[` `]` | ouverture / fermeture d'un bloc « système » |
| `FR(` `)FR`   | `(` `)` | ouverture / fermeture d'un cadre « fictionnel » |

### 4.2 Pour le volet « arbres » (jour 3)

Un *prompt* parenthésé devient un **terme** sur un alphabet gradué : feuilles
`txt, enc, ovr, role` (arité 0), nœuds `seq` (arité 2), `sys`, `frame` (arité 1).

### 4.3 Pour le volet « calcul » (jour 4)

Les entiers sont en **unaire** : `n` ↦ `1ⁿ` (donc `0` = mot vide). Les opérandes
sont séparées par `+ - * /`. Le symbole blanc est `_`.

---

## 5. ⚠️ Cadre éthique (volet Shield) — non négociable

Le volet Shield porte **exclusivement** sur la **structure formelle** que
reconnaît un système de **défense**. On ne manipule **aucun contenu nuisible** :
tous les *prompts* sont des suites de **jetons abstraits**. L'objectif
pédagogique — automates, grammaires, transducteurs, arbres — est atteint **sans
jamais écrire la moindre attaque réelle**. C'est précisément la philosophie de la
sécurité **défensive**.

> **Tout rendu contenant un exemple d'attaque réelle est hors-sujet et pénalisé.**

---

## 6. Organisation de la semaine

| Jour | Fiche | Cœur produit | Tests cibles |
|---|---|---|---|
| 1 | `jour1_regulier.md` | `dfa`, `nfa`, `fst` + détecteur, normaliseur | `test_regular.py` |
| 2 | `jour2_horscontexte.md` | `pda`, `cfg` + délimiteurs | `test_cfg_nerode.py` (CFG), `test_regular.py` (PDA) |
| 3 | `jour3_arbres.md` | `tree` + automate morpho + AttackDecomposer | `test_tree.py` |
| 4 | `jour4_calculabilite.md` | `turing`, `utm` + calculatrice | `test_turing.py`, `test_calc.py` |
| 5 | `jour5_integration.md` | `pipeline`, `myhill_nerode` | `test_pipeline.py`, `test_cfg_nerode.py` |

Chaque fiche contient : un **encadré contexte**, des **questions de théorie
(`Q…`)** et de **pratique (`E…`)** numérotées et **notées**, les **diagrammes /
tables** attendus, les **sorties console de référence**, un **mini-barème du
jour** et des **références**.

---

## 7. Barème global (sur 20, + 6 bonus)

| Jour | Thème | Points |
|---|---|---:|
| 1 | Régulier & transducteurs (AFD/AFN, FST, miroir) | 4 |
| 2 | Hors-contexte (pompage, CFG, PDA) | 4 |
| 3 | **Automates d'arbres** (BUTA, morpho + Shield, produit) | 5 |
| 4 | Calculabilité (MT, MTU, calculatrice, indécidabilité) | 4 |
| 5 | Intégration & Myhill–Nerode (pipeline, minimisation) | 3 |
| **Total** | | **20** |
| Bonus | regex/Thompson, CFG/CYK, hash-consing, produit d'arbres, variante C++ | +6 |

**Critères transverses (inclus dans les points ci-dessus) :** rigueur des
justifications, qualité des automates/arbres dessinés, **tests qui passent**, et
**architecture** (les apps instancient le cœur, sans le réécrire).

**Deux règles « gate » (pénalité forte si non respectées) :**
- *Anti-copier-coller :* une app qui **redéfinit** un automate au lieu
  d'instancier celui de `formlang` perd les points d'intégration.
- *Honnêteté intellectuelle :* toute borne de complexité doit être **démontrée
  ou référencée** (pas de constante « de mémoire »). Reportez vos **vrais**
  chiffres de sortie, même modestes.

---

## 8. Livrables & modalités de rendu

1. **Dépôt Git** `NOM1_NOM2_formlang/` contenant :
   - `formlang/`, `apps/`, `pipeline.py`, `tests/` complétés et **qui passent** :
     `pytest -q` doit afficher `… passed` ;
   - les sorties console : `pytest -q > out_tests.txt` et
     `python pipeline.py > out_demo.txt` (+ modes `--word`, `--morpho`).
2. **Rapport** (PDF, gabarit `RAPPORT_TEMPLATE.md`) : pour chaque jour, les
   réponses aux `Q…`, les preuves demandées, les diagrammes, et les chiffres
   mesurés.
3. **Soutenance** (10 min) : démonstration **bout-en-bout** (`pipeline.py`) +
   un cas par étage + difficultés rencontrées.

Le code doit s'exécuter avec **Python 3.10+ et `pytest` seulement** (aucune autre
dépendance).

---

## 9. Pré-requis (acquis du cours)

Langages formels ; expressions régulières ; grammaires ; automates finis
(AFD/AFN) ; déterminisation ; minimisation ; notions de calculabilité. Le projet
**introduit** les automates d'arbres comme généralisation des automates finis,
et la machine universelle comme aboutissement.

---

## 10. Références (toutes réelles)

- H. Comon *et al.*, *Tree Automata Techniques and Applications* (TATA), 2007 —
  automates d'arbres, déterminisation, clôtures, minimisation.
- J. Daciuk, S. Mihov, B. Watson, R. Watson, *Incremental construction of
  minimal acyclic finite-state automata*, **Computational Linguistics** 26(1),
  2000 — dictionnaires morphologiques minimaux.
- J.-C. Filliâtre, S. Conchon, *Type-safe modular hash-consing*, ML Workshop,
  2006.
- J. Hopcroft, R. Motwani, J. Ullman, *Introduction to Automata Theory,
  Languages, and Computation* — réguliers, pompage, Myhill–Nerode, minimisation.
- M. Sipser, *Introduction to the Theory of Computation* — machine universelle,
  indécidabilité de l'arrêt, réductions. *(Vérifiez-y toute borne de complexité
  avant de la citer comme un fait : le surcoût exact de la simulation
  universelle ne doit pas être donné « de mémoire ».)*

---

*Fin du chapeau. Passez à la fiche `jour1_regulier.md`.*


