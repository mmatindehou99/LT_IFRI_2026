# TP — Théorie des langages appliquée au moteur **LLM-Secure Shield**

**Établissement :** IFRI — Master Génie Logiciel
**Module :** Théorie des langages (langages formels, expressions régulières, grammaires, automates finis)
**Durée conseillée :** 2 séances de 3 h + travail personnel
**Auteur du sujet :** Dr. Mêton Mêton ATINDEHOU — projet *Algorithmic Singularity*

> ⚠️ **Cadre éthique et légal.** Ce TP porte exclusivement sur la **structure formelle** que reconnaît un système de **défense**. On ne manipule **aucun contenu nuisible** : tous les *prompts* sont représentés par des **jetons abstraits** (`TXT`, `OVR`, `ROLE`, `ENC`, délimiteurs). L'objectif pédagogique — automates, grammaires, transducteurs, automates d'arbres — est atteint sans jamais écrire la moindre attaque réelle. C'est précisément la philosophie de la sécurité *défensive* enseignée en Master.

---

## 1. Contexte : qu'est-ce que LLM-Secure et le Shield ?

### 1.1 Le problème

Un **grand modèle de langage** (LLM) suit des règles de comportement. Un *prompt* (message de l'utilisateur) malveillant tente de **contourner** ces règles : annuler les instructions système, réassigner un rôle au modèle, masquer une intention par un encodage, ou forger de faux délimiteurs système.

### 1.2 La solution : LLM-Secure Shield

**LLM-Secure** est une bibliothèque de sécurité pour LLM. Son composant **Shield** analyse chaque *prompt* entrant et décide s'il faut le **laisser passer** ou le **bloquer**.

Particularité essentielle pour ce cours : **le Shield n'utilise pas d'apprentissage automatique**. Il repose sur des **méthodes algorithmiques déterministes**, qui sont exactement des objets de la théorie des langages :

| Méthode du Shield | Outil formel | Reconnaît… |
|---|---|---|
| `EnhancedNormalizer` | **Transducteur fini (FST)** | une relation de normalisation (leet, casse…) |
| `SingularityDetector` | **Expression régulière / AFD** | la présence de jetons de contrôle |
| Détection de délimiteurs | **Grammaire hors-contexte / automate à pile** | l'imbrication (bien/mal) formée de blocs |
| `AttackDecomposer` | **Automate d'arbres (bottom-up)** | une configuration dangereuse dans l'**arbre** |
| `CongruenceClassifier` | **Congruence de Myhill-Nerode** | les classes d'équivalence de *prompts* |

**Idée directrice du TP :** un *prompt* devient suspect non pas à cause d'un mot, mais à cause d'une **structure**. Or « reconnaître une structure » est exactement ce que font automates et grammaires. Chaque partie du TP reconstruit une couche du Shield avec l'outil formel adéquat, en montant la **hiérarchie de Chomsky**, jusqu'aux **automates d'arbres**.

---

## 2. Modèle abstrait commun (à lire avant tout)

On ne travaille jamais sur du texte réel. Un *prompt* est une **suite de lexèmes** (jetons) sur l'alphabet :

| Jeton | Symbole court | Signification (bénigne) |
|---|---|---|
| `TXT`  | `a` | texte ordinaire, anodin |
| `OVR`  | `o` | marqueur d'**annulation** d'instruction |
| `ROLE` | `r` | marqueur de **réassignation de rôle** |
| `ENC`  | `e` | bloc **encodé / obfusqué** |
| `SYS[` | `[` | **ouverture** d'un bloc « système » |
| `]SYS` | `]` | **fermeture** d'un bloc « système » |
| `FR(`  | `(` | **ouverture** d'un **cadre fictionnel** (« hypothèse », « roman ») |
| `)FR`  | `)` | **fermeture** d'un cadre fictionnel |

- Pour les **Parties 1, 2, 5**, on se limite à l'alphabet de mots `Σ = {a, o, r, e}`.
- Pour les **Parties 3, 4**, on ajoute les délimiteurs `[ ] ( )`.

Un jeton seul n'a rien de nuisible : `o` signale simplement *« ici se trouve une formulation d'annulation »*. C'est l'**agencement** des jetons qui est analysé.

---

## Partie 1 — Expressions régulières & AFD : le `SingularityDetector` (4 pts)

Le `SingularityDetector` repère des **jetons de contrôle** par expressions régulières. On modélise ici sa version la plus simple.

On considère `Σ = {a, o, r}`. Un *prompt* est dit **« à inversion directe »** s'il **annule une instruction puis réassigne un rôle**, c'est-à-dire s'il contient le **facteur** `or` (un `o` immédiatement suivi d'un `r`).

Soit le langage
$$L_1 = \{\, w \in \Sigma^\* \mid w \text{ contient le facteur } \mathtt{or} \,\}.$$

**Questions**

1.1. Donner une **expression régulière** dénotant $L_1$. (0,5)

1.2. Construire un **automate fini non déterministe** (AFN) reconnaissant $L_1$ à partir de votre expression régulière (méthode de Thompson ou directe). (1)

1.3. **Déterminiser** cet AFN (algorithme des sous-ensembles). Donner la table de transition de l'AFD obtenu. (1)

1.4. **Minimiser** l'AFD (algorithme de Moore / Hopcroft). Combien d'états dans l'automate minimal ? (1)

1.5. Le Shield veut aussi détecter le motif « annulation **n'importe où avant** une réassignation » : $L_1' = \{ w \mid w \text{ contient un } \mathtt{o} \text{ suivi (pas forcément immédiatement) d'un } \mathtt{r}\}$. Donner l'expression régulière de $L_1'$ et expliquer en une phrase la différence avec $L_1$. (0,5)

---

## Partie 2 — Transducteurs finis : le `EnhancedNormalizer` (4 pts)

Avant toute détection, le Shield **normalise** le texte pour défaire les obfuscations (« leetspeak », casse…). Une normalisation est une **relation rationnelle**, réalisée par un **transducteur fini**.

On définit la normalisation *leet* par la fonction sur les symboles :
$$\tau(\mathtt{4})=\mathtt{a},\ \tau(\mathtt{3})=\mathtt{e},\ \tau(\mathtt{0})=\mathtt{o},\ \tau(\mathtt{1})=\mathtt{i},\ \tau(\mathtt{5})=\mathtt{s},$$
et $\tau(x)=x$ pour tout autre symbole.

**Questions**

2.1. Construire un **transducteur fini** $T$ (à un seul état suffira) réalisant la normalisation *leet* lettre par lettre. Donner ses transitions sous la forme `état --entrée/sortie--> état`. (1)

2.2. Calculer $T(\texttt{"4tt4ck"})$ et $T(\texttt{"r0le"})$. (0,5)

2.3. Montrer que $T$ est **idempotent** sur les sorties : pour tout mot $w$, $T(T(w)) = T(w)$. Justifier formellement (indication : l'image de $\tau$ ne contient aucun chiffre *leet*). (1)

2.4. **Question théorique (importante).** Le Shield gère aussi le **texte inversé** (lecture à l'envers). La transduction « miroir » $w \mapsto w^{R}$ (renversement) est-elle réalisable par un transducteur fini **à une passe** (one-way) ? Justifier. *(Indication : pensez à la mémoire nécessaire ; comparez avec un transducteur **bidirectionnel** (two-way).)* (1,5)

---

## Partie 3 — Grammaires hors-contexte & automate à pile : les délimiteurs (4 pts)

Les attaques par **faux délimiteurs** imitent un bloc système `[ … ]` ou un cadre fictionnel `( … )`, éventuellement **imbriqués**. Reconnaître l'imbrication **bien formée** dépasse le pouvoir des automates finis : c'est un **langage hors-contexte** (parent du langage de Dyck).

On travaille sur `Σ₃ = {a, o, r, [, ], (, )}`. Un *prompt* est **bien parenthésé** si tous les blocs `[…]` et cadres `(…)` sont correctement ouverts/fermés et imbriqués (pas de chevauchement).

**Questions**

3.1. Soit le langage $D = \{\,\mathtt{[}^n\,\mathtt{]}^n \mid n \ge 0\,\}$ (blocs système purement imbriqués). Montrer, à l'aide du **lemme de l'étoile** (*pumping lemma*) pour les langages réguliers, que $D$ **n'est pas régulier**. Conclure que la détection d'imbrication **ne peut pas** se faire avec le seul `SingularityDetector` (AFD). (1,5)

3.2. Donner une **grammaire hors-contexte** $G$ engendrant l'ensemble des *prompts* **bien parenthésés** sur `Σ₃` (les jetons `a, o, r` pouvant apparaître librement entre les délimiteurs). (1)

3.3. Votre grammaire est-elle **ambiguë** ? Si oui, donner deux arbres de dérivation pour un même mot ; sinon, justifier. (0,5)

3.4. Décrire un **automate à pile** (PDA) reconnaissant les *prompts* bien parenthésés (acceptation par pile vide). Donner la fonction de transition. (1)

---

## Partie 4 — 🌳 Automates d'arbres : l'`AttackDecomposer` (6 pts) — **cœur du TP**

C'est ici que la structure prend tout son sens. Le `AttackDecomposer` ne lit pas le *prompt* de gauche à droite : il le **décompose en arbre** (l'arbre de dérivation de la Partie 3), puis décide si une **configuration dangereuse** apparaît dans cet arbre. On utilise un **automate d'arbres ascendant** (*bottom-up tree automaton*).

### 4.1 Alphabet gradué (ranked alphabet)

On représente un *prompt* parenthésé par un **terme** sur l'alphabet gradué $\mathcal{F}$ :

| Symbole | Arité | Rôle |
|---|---|---|
| `txt`, `ovr`, `role`, `enc` | 0 | feuilles (un jeton `a`, `o`, `r`, `e`) |
| `seq` | 2 | concaténation de deux sous-prompts |
| `sys` | 1 | bloc système `[ … ]` autour de son contenu |
| `frame` | 1 | cadre fictionnel `( … )` autour de son contenu |

**Exemple.** Le *prompt* `[ r ]` (« un marqueur de rôle **dans** un bloc système ») se représente par le terme :
```
sys( role )
```
Le *prompt* `( r ) a` se représente par :
```
seq( frame(role), txt )
```

### 4.2 L'automate d'arbres du Shield

On définit l'**automate d'arbres ascendant déterministe** $\mathcal{A} = (Q, \mathcal{F}, Q_f, \Delta)$ avec :

- États : $Q = \{q_{\text{safe}},\ q_{\text{ovr}},\ q_{\text{role}},\ q_{\text{danger}}\}$
- États acceptants (= **bloquer**) : $Q_f = \{q_{\text{danger}}\}$
- Règles de transition $\Delta$ (lecture **des feuilles vers la racine**) :

```
(F1)  txt          → q_safe
(F2)  enc          → q_safe
(F3)  ovr          → q_ovr
(F4)  role         → q_role

(S1)  seq(q_danger, _)  → q_danger          ; le danger remonte
(S2)  seq(_, q_danger)  → q_danger
(S3)  seq(q_ovr,  q_role) → q_danger        ; annulation PUIS rôle au même niveau
(S4)  seq(q_role, q_ovr)  → q_danger
(S5)  seq(x, y)    → fusion(x, y)           ; sinon, état « le plus sévère »
                                            ; ordre : safe < ovr < role

(C1)  frame(q_role)   → q_danger            ; rôle réassigné DANS une fiction
(C2)  frame(q_ovr)    → q_danger            ; annulation DANS une fiction
(C3)  frame(q_safe)   → q_safe
(C4)  frame(q_danger) → q_danger

(B1)  sys(q_role)   → q_danger              ; rôle DANS un faux bloc système
(B2)  sys(q_ovr)    → q_danger              ; annulation DANS un faux bloc système
(B3)  sys(q_safe)   → q_safe
(B4)  sys(q_danger) → q_danger
```

où `fusion` (règle S5) renvoie l'état le plus sévère selon `safe < ovr < role` (jamais `danger`, ce cas étant traité par S1-S4).

**Lecture sémantique.** Un `OVR` ou un `ROLE` **isolé** n'est *pas* bloqué (un utilisateur peut légitimement écrire « ignore le bruit » ou « joue le rôle d'un poète »). Il devient **dangereux** uniquement quand il est **imbriqué** sous un bloc système forgé (`sys`) ou un cadre fictionnel (`frame`), ou combiné à son complément au même niveau (`seq`). **C'est la hiérarchie — l'arbre — qui décide**, pas la simple présence d'un jeton.

### 4.3 Questions

4.1. Donner le **terme** (arbre) correspondant à chacun des *prompts* suivants, puis exécuter $\mathcal{A}$ **de bas en haut** en indiquant l'état de chaque nœud. Le *prompt* est-il **bloqué** ? (2)
- (a) `a a` → `seq(txt, txt)`
- (b) `r` (rôle isolé) → `role`
- (c) `[ r ]` → `sys(role)`
- (d) `( o ) a` → `seq(frame(ovr), txt)`
- (e) `[ a ( r ) ]` → `sys( seq(txt, frame(role)) )`

4.2. L'automate $\mathcal{A}$ est-il **déterministe** ? **Complet** ? Justifier en une phrase chacun. (1)

4.3. **Pourquoi un automate de mots ne suffit pas.** Expliquer pourquoi la propriété « un `ROLE` apparaît **à l'intérieur** d'un bloc système » ne peut **pas** être décidée par un AFD lisant le mot de gauche à droite, alors qu'elle l'est trivialement par $\mathcal{A}$. (Relier à la Partie 3.) (1)

4.4. **Théorème du *yield* (frontière).** On admet que la **frontière** (mot des feuilles, de gauche à droite) d'un langage d'arbres régulier est un langage **hors-contexte**. Illustrer : donner la frontière des termes (c), (d), (e) ci-dessus, et expliquer le lien avec la grammaire de la Partie 3. (1)

4.5. **Composition de détecteurs = produit d'automates.** Le Shield combine plusieurs détecteurs. On admet que les langages d'arbres réguliers sont **clos par intersection** (produit cartésien des états). Décrire en quelques lignes comment combiner $\mathcal{A}$ avec un second automate d'arbres $\mathcal{A}_{\text{enc}}$ (qui bloque tout arbre contenant **au moins deux** feuilles `enc`) pour obtenir un détecteur « dangereux **ET** doublement encodé ». (1)

---

## Partie 5 — Congruence & minimisation : le `CongruenceClassifier` (bonus, 2 pts)

Le `CongruenceClassifier` regroupe les *prompts* **équivalents** sous une même **forme canonique**. C'est exactement la **congruence de Myhill-Nerode**.

5.1. Rappeler la définition de la congruence (relation d'équivalence **invariante à droite**) $\sim_L$ associée à un langage $L$. (0,5)

5.2. Pour le langage $L_1$ de la Partie 1, déterminer les **classes d'équivalence** de $\sim_{L_1}$. Combien y en a-t-il ? Relier ce nombre à la taille de l'AFD **minimal** trouvé en 1.4 (théorème de Myhill-Nerode). (1)

5.3. **Ouverture.** Il existe une congruence de Myhill-Nerode pour les **automates d'arbres** (sur les *contextes* plutôt que les suffixes). En une phrase, expliquer ce que serait alors une « forme canonique » de *prompt* pour le Shield. (0,5)

---

## Barème (sur 20, + 2 bonus)

| Partie | Thème | Points |
|---|---|---|
| 1 | Expr. régulières & AFD (`SingularityDetector`) | 4 |
| 2 | Transducteurs (`EnhancedNormalizer`) | 4 |
| 3 | Grammaires & automate à pile (délimiteurs) | 4 |
| 4 | **Automates d'arbres (`AttackDecomposer`)** | 6 |
| 5 | Congruence & minimisation (bonus) | +2 |
| **Total** | | **18 (+2)** |

*Critères transverses (2 pts inclus dans les parties) : rigueur des justifications, clarté des automates/arbres dessinés, et qualité du code rendu (Partie technique).*

---

## Livrables

1. Un **rapport** (PDF) avec automates, grammaires, arbres dessinés et justifications.
2. Le **code** complété du squelette `squelette_tp_shield.py` (voir fichier joint), qui doit passer les tests fournis :
   - `dfa_L1(w)` — reconnaisseur de $L_1$ (Partie 1)
   - `leet_normalize(w)` — transducteur (Partie 2)
   - `well_parenthesized(w)` — automate à pile (Partie 3)
   - `tree_automaton(term)` — automate d'arbres ascendant (Partie 4) **[noté double]**

> Rappel éthique : aucun rendu ne doit contenir d'exemple d'attaque réelle. Tout est exprimé sur l'alphabet abstrait `{a, o, r, e, [, ], (, )}`.
