# CORRIGÉ ENSEIGNANT — TP Théorie des langages / LLM-Secure Shield

> Document réservé à l'enseignant. Toutes les solutions utilisent l'alphabet abstrait
> `Σ = {a, o, r, e, [, ], (, )}` — aucun contenu sensible.

---

## Partie 1 — Expressions régulières & AFD (4 pts)

**1.1 Expression régulière de $L_1$** (facteur `or`), sur `Σ = {a,o,r}` :
$$(a\,|\,o\,|\,r)^\*\ \mathtt{o}\,\mathtt{r}\ (a\,|\,o\,|\,r)^\*$$

**1.2 AFN** (construction directe). États $\{0,1,2\}$, initial $0$, final $2$ :

```
        a,o,r                       a,o,r
        ┌──┐                        ┌──┐
        ▼  │            o           ▼  │
   ──▶ (0)─┘ ───────────────▶ (1) ──── r ──▶ ((2))
        │                       ▲
        └───────── o ───────────┘   (boucle: sur 'o' on peut rester "armé")
```
Transitions : $\delta(0,a)=\{0\}$, $\delta(0,o)=\{0,1\}$, $\delta(0,r)=\{0\}$, $\delta(1,r)=\{2\}$ (et $\delta(1,o)=\{1\}$ si l'on autorise une nouvelle tentative), $\delta(2,\cdot)=\{2\}$.

**1.3 Déterminisation (sous-ensembles).** AFD à 3 états utiles
$A=\{0\}$ (init), $B=\{0,1\}$, $C=\{0,1,2\}$ (final) :

| état | `a` | `o` | `r` |
|---|---|---|---|
| **A** = {0} | A | B | A |
| **B** = {0,1} | A | B | **C** |
| **C** = {0,1,2} (final) | C | C | C |

Lecture : on passe en `B` dès qu'on voit un `o` (« armé »), on tombe en `C` (accepté, absorbant) si un `r` suit immédiatement ; tout `a` après un `o` non suivi de `r` désarme (retour `A`).

**1.4 Minimisation.** Les trois états sont déjà distinguables :
`C` est final, `A` et `B` non ; `A` et `B` diffèrent sur l'entrée `r` (`A→A` non final, `B→C` final). **L'AFD minimal a donc 3 états.**

**1.5** $L_1'$ (un `o` puis, plus loin, un `r`) :
$$(a\,|\,o\,|\,r)^\*\ \mathtt{o}\ (a\,|\,o\,|\,r)^\*\ \mathtt{r}\ (a\,|\,o\,|\,r)^\*$$
Différence : $L_1$ exige l'**adjacence** `o`·`r` (facteur), $L_1'$ accepte n'importe quel `o` **précédant** un `r` (sous-séquence). On a $L_1 \subsetneq L_1'$.

---

## Partie 2 — Transducteurs finis (4 pts)

**2.1 Transducteur $T$** à un seul état $q_0$ (initial et final) :
```
q0 --4/a--> q0     q0 --3/e--> q0     q0 --0/o--> q0
q0 --1/i--> q0     q0 --5/s--> q0     q0 --x/x--> q0   (pour tout autre x)
```
C'est une fonction séquentielle (lettre à lettre), donc une relation rationnelle.

**2.2** $T(\texttt{"4tt4ck"}) = \texttt{"attack"}$ ; $T(\texttt{"r0le"}) = \texttt{"role"}$.

**2.3 Idempotence.** Soit $\Delta=\{4,3,0,1,5\}$ l'ensemble des chiffres *leet*. Par définition, l'image $\tau(x)\in\{a,e,o,i,s\}\cup(\Sigma\setminus\Delta)$ ne contient **aucun** élément de $\Delta$. Donc pour tout symbole de sortie $y=\tau(x)$, on a $y\notin\Delta$, d'où $\tau(y)=y$. Comme $T$ applique $\tau$ lettre à lettre, $T(T(w))=T(w)$ pour tout $w$. $\blacksquare$

**2.4 Renversement $w\mapsto w^R$.**
- **One-way FST : impossible.** Un transducteur fini à une passe lit l'entrée de gauche à droite et émet au fur et à mesure avec une **mémoire bornée** (états finis). Produire $w^R$ exige de **mémoriser tout $w$** avant d'émettre la première lettre de sortie (la dernière lettre lue). La quantité d'information à retenir croît avec $|w|$ : c'est impossible avec un nombre fini d'états. (Argument type : si c'était possible, sur l'alphabet $\{0,1\}$, deux mots distincts de même longueur $> |Q|$ partageraient un état après lecture, forçant la même suite de sorties restantes — contradiction.)
- **Two-way FST : possible.** Une tête de lecture bidirectionnelle peut aller jusqu'à la fin du ruban puis le relire de droite à gauche en émettant — d'où $w^R$. Le renversement est une transduction **rationnelle bidirectionnelle**, pas one-way.
- *Conséquence pour le Shield :* la dé-inversion n'est pas une simple normalisation séquentielle ; le code la traite par un passage dédié (renversement explicite de la chaîne), ce qui correspond bien à une opération two-way.

*(Barème : 0,75 pour « one-way impossible » + argument ; 0,75 pour « two-way possible ».)*

---

## Partie 3 — Grammaires & automate à pile (4 pts)

**3.1 $D=\{[^n\,]^n\}$ n'est pas régulier (lemme de l'étoile).**
Supposons $D$ régulier, de constante de pompage $p$. Prenons $w=[^p\,]^p\in D$, $|w|\ge p$. Toute décomposition $w=xyz$ avec $|xy|\le p$, $|y|\ge1$ a $y=[^k$ ($k\ge1$) entièrement dans le bloc de `[`. Alors $xy^2z=[^{p+k}\,]^p\notin D$ (déséquilibre). Contradiction. Donc **$D$ n'est pas régulier**. Comme un AFD reconnaît exactement les langages réguliers, le `SingularityDetector` (AFD) **ne peut pas** vérifier l'équilibre/imbrication des délimiteurs. $\blacksquare$

**3.2 Grammaire hors-contexte $G$** des *prompts* bien parenthésés sur `Σ₃` :
```
S → S S        (concaténation)
S → [ S ]      (bloc système)
S → ( S )      (cadre fictionnel)
S → a | o | r  (jetons libres)
S → ε          (vide)
```
$G$ engendre tous les mots à délimiteurs `[],()` bien imbriqués, mêlés librement de `a,o,r`.

**3.3 Ambiguïté.** $G$ est **ambiguë** à cause de `S → S S` (concaténation non associée). Exemple : `a a a` admet (au moins) deux arbres — `S(S(a) S(S(a) S(a)))` et `S(S(S(a) S(a)) S(a))`. On peut désambiguïser en imposant une associativité, p. ex. :
```
S → T S | T          T → [ S ] | ( S ) | a | o | r | ε
```

**3.4 Automate à pile (acceptation par pile vide).**
$P=(\{q\},\ \Sigma_3,\ \Gamma,\ \delta,\ q,\ Z_0)$ avec $\Gamma=\{Z_0,\#_[,\#_(\}$ :
```
δ(q, [, X)      = (q, #[ X)      empiler un témoin de '['
δ(q, (, X)      = (q, #( X)      empiler un témoin de '('
δ(q, ], #[ )    = (q, ε)         dépiler sur ']' si sommet = #[
δ(q, ), #( )    = (q, ε)         dépiler sur ')' si sommet = #(
δ(q, a, X)      = (q, X)         a,o,r : pile inchangée
δ(q, o, X)      = (q, X)
δ(q, r, X)      = (q, X)
δ(q, ε, Z0)     = (q, ε)         vider Z0 en fin (acceptation pile vide)
```
Le mot est accepté ssi tous les délimiteurs s'apparient correctement (pile vide à la fin). Une fermeture sans ouverture correspondante (`]` avec sommet ≠ `#[`) bloque → rejet.

---

## Partie 4 — Automates d'arbres (6 pts) — cœur

**4.1 Exécutions ascendantes.**

| | Terme | Calcul des états (bas → haut) | Racine | Bloqué ? |
|---|---|---|---|---|
| (a) | `seq(txt, txt)` | txt→q_safe, txt→q_safe ; seq(safe,safe)→**q_safe** (S5) | q_safe | **Non** |
| (b) | `role` | role→**q_role** (F4) | q_role | **Non** (q_role ∉ Q_f) |
| (c) | `sys(role)` | role→q_role ; sys(q_role)→**q_danger** (B1) | q_danger | **OUI** |
| (d) | `seq(frame(ovr), txt)` | ovr→q_ovr ; frame(q_ovr)→q_danger (C2) ; seq(q_danger, q_safe)→**q_danger** (S1) | q_danger | **OUI** |
| (e) | `sys(seq(txt, frame(role)))` | txt→q_safe ; role→q_role ; frame(q_role)→q_danger (C1) ; seq(q_safe,q_danger)→q_danger (S2) ; sys(q_danger)→**q_danger** (B4) | q_danger | **OUI** |

Remarque pédagogique : (b) montre qu'un **rôle isolé n'est pas bloqué** ; (c)(e) montrent que **le même `role` devient dangereux par imbrication**. C'est tout l'intérêt de l'arbre.

**4.2 Déterminisme / complétude.**
- **Déterministe** : oui — pour chaque symbole et chaque tuple d'états-fils, **au plus une** règle s'applique (les cas S1-S4 sont disjoints de S5 par priorité, et frame/sys couvrent chaque état une seule fois). C'est un **DFTA**.
- **Complet** : oui — toute combinaison (symbole, états-fils) reçoit une image (S5 sert de cas par défaut pour `seq` ; chaque règle frame/sys couvre les 4 états). Aucun blocage par absence de transition.

**4.3 Pourquoi un AFD de mots échoue.**
La propriété « il existe un `r` **situé à l'intérieur** d'un bloc `[ … ]` » dépend de l'**imbrication** : il faut savoir, au moment où on lit `r`, si l'on est **à l'intérieur** d'un `[` non encore fermé, c.-à-d. compter la profondeur de parenthésage. Cela exige une **pile** (cf. Partie 3) ou, de manière équivalente sur la structure, un **automate d'arbres**. Un AFD a une mémoire bornée et ne peut pas suivre une profondeur d'imbrication non bornée : il ne reconnaît que des langages réguliers, or « rôle imbriqué dans un bloc » n'est pas régulier (même argument de pompage que 3.1).

**4.4 Frontières (*yields*).**
- (c) `sys(role)` → frontière `r` (le bloc système entoure un `r`) → mot délimité `[ r ]`.
- (d) `seq(frame(ovr), txt)` → frontière `( o ) a`.
- (e) `sys(seq(txt, frame(role)))` → frontière `[ a ( r ) ]`.

Lien : ces frontières sont **exactement** des mots engendrés par la grammaire $G$ de la Partie 3. Le théorème admis dit que l'ensemble des frontières des arbres acceptés par un automate d'arbres régulier forme un **langage hors-contexte** — d'où la correspondance *automate d'arbres ↔ grammaire hors-contexte*.

**4.5 Produit d'automates (intersection).**
On construit l'automate produit $\mathcal{A}\times\mathcal{A}_{\text{enc}}$ dont les états sont des **paires** $(p,q)$ avec $p\in Q_\mathcal{A}$ et $q\in Q_{\mathcal{A}_{\text{enc}}}$ (ce dernier comptant $0,1,\ge2$ feuilles `enc`, p. ex. $q\in\{0,1,2^+\}$). Chaque règle s'applique **composante par composante** : pour `seq((p_1,q_1),(p_2,q_2))`, on calcule séparément l'état $\mathcal{A}$ et l'état de comptage `enc` (somme plafonnée à $2^+$). Les états **acceptants** du produit sont $\{(q_{\text{danger}},\,2^+)\}$. On bloque donc **uniquement** les arbres à la fois dangereux **et** doublement encodés. (Clôture par intersection des langages d'arbres réguliers.)

---

## Partie 5 — Congruence & minimisation (bonus, 2 pts)

**5.1** $u \sim_L v \iff \forall w\in\Sigma^\*,\ (uw\in L \Leftrightarrow vw\in L)$. C'est une relation d'équivalence **invariante à droite** ($u\sim_L v \Rightarrow ua\sim_L va$).

**5.2 Classes de $\sim_{L_1}$.** Trois classes, correspondant aux trois états de l'AFD minimal :
- $C_A$ : mots **sans** facteur `or` et **ne se terminant pas** par un `o` « armé » → état A ;
- $C_B$ : mots sans facteur `or` mais **se terminant par un `o`** en attente d'un `r` → état B ;
- $C_C$ : mots **contenant déjà** le facteur `or` → état C (absorbant).

Il y a **3 classes**, ce qui égale le nombre d'états de l'AFD minimal de 1.4 : c'est le **théorème de Myhill-Nerode** (l'indice de $\sim_L$ = nombre d'états de l'automate minimal).

**5.3 Ouverture (Myhill-Nerode pour arbres).** La congruence s'exprime alors sur les **contextes** (arbres « à trou ») : deux sous-arbres sont équivalents s'ils mènent au même verdict **dans tout contexte**. Une **forme canonique** de *prompt* serait son arbre **minimal** modulo cette congruence — c'est exactement ce que vise le `CongruenceClassifier` : ramener des *prompts* structurellement équivalents à un unique représentant pour décider une seule fois.

---

## Notes de correction

- **Partie 4 prioritaire** (6 pts + double pondération du code) : c'est l'objectif d'apprentissage central (généraliser mots → arbres). Valoriser toute exécution ascendante correcte même si une règle est mal nommée.
- Accepter toute variante d'AFN/AFD/grammaire **équivalente**.
- En 2.4 et 4.3, l'essentiel est l'**argument de mémoire bornée** (pompage / nombre fini d'états), pas la forme exacte.
- Pénaliser tout rendu contenant un exemple d'attaque réelle (hors-sujet **et** hors-cadre éthique) — rappeler que le TP est purement structurel.
