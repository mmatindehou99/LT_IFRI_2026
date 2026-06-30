# TP (niveau Master) — Machine de Turing Universelle et calculatrice arithmétique unaire

**Module :** Calculabilité & Théorie des langages
**Modalités :** binôme — rapport théorique + notebook exécutable + soutenance
**Pondération indicative :** Théorie 40 % · Implémentation 45 % · Explication des tables & soutenance 15 %

> Objectif pédagogique : comprendre *pourquoi une seule machine suffit à toutes les calculer*, l'implémenter, puis construire une calculatrice arithmétique **en vraies machines de Turing** (alphabet unaire) exécutées **par la MTU**, et **savoir expliquer chaque ligne d'une table de transition**.

---

## PARTIE I — Aspects théoriques

### 1. Définitions de référence

Une machine de Turing déterministe est un septuplet
**M = (Q, Σ, Γ, δ, q₀, ␣, F)** avec δ : Q × Γ → Q × Γ × {L, R, S}.
Une **configuration** est notée *α q β* (contenu à gauche de la tête, état courant, contenu sous/à droite de la tête). Le calcul est la suite C₀ ⊢ C₁ ⊢ … et M accepte *w* si (q₀, w) ⊢\* (q_f, …) avec q_f ∈ F.

### 2. Machine de Turing universelle U

**Définition.** Une MTU U est une machine telle que, pour toute MT M et tout mot w :

> U(⟨M⟩ ## w) « se comporte comme » M(w) : U accepte ⟨M⟩##w ⟺ M accepte w, et le ruban final de U code le ruban final de M.

U prend donc en entrée **une donnée qui est elle-même un programme** (⟨M⟩) : c'est le principe du **programme enregistré** (von Neumann), et l'ancêtre conceptuel de l'interpréteur.

**Questions à traiter (rédaction rigoureuse exigée) :**

1.1 Donner un **schéma d'encodage** ⟨M⟩ : numérotation des états, des symboles, et linéarisation de δ en une liste de quintuplets `(q, a) → (q', b, d)`. Justifier que l'encodage est **injectif** et **décidable** (on peut reconstruire M à partir de ⟨M⟩).

1.2 Décrire l'**invariant de simulation** de U : à tout instant, U maintient sur son ruban (i) la description ⟨M⟩ figée, (ii) l'état courant simulé, (iii) le contenu du ruban simulé, (iv) la position de la tête simulée. Décrire un *cycle* de simulation (lire le symbole simulé → chercher la transition dans ⟨M⟩ → écrire → déplacer → mettre à jour l'état).

1.3 **Thèse de Church–Turing** : énoncer la thèse, préciser que ce n'est *pas* un théorème, et citer ≥ 2 modèles équivalents (λ-calcul, fonctions récursives, machines RAM) comme faisceau d'arguments.

1.4 **Surcoût de la simulation (à discuter, sans surenchère sur les constantes).** Si M effectue *t* étapes :
- une MTU **multi-ruban** peut simuler M en O(t · |⟨M⟩|) (recherche de transition à coût borné par la taille de la description) ;
- la réduction multi-ruban → mono-ruban coûte au plus un facteur quadratique (T(n) ⟶ O(T(n)²)) ;
- *Résultat classique à citer* (Hennie–Stearns) : un ralentissement seulement logarithmique est atteignable par une simulation multi-ruban soignée. **Citer la source et ne pas affirmer de constante exacte.**

1.5 **Limites.** Montrer (réduction depuis HALT) que « U s'arrête sur ⟨M⟩##w » est **indécidable** : l'universalité n'implique pas l'omniscience.

> ⚠️ *Consigne d'honnêteté intellectuelle (notée) :* toute affirmation de complexité doit être soit démontrée, soit accompagnée d'une référence ; les bornes « folkloriques » non sourcées sont pénalisées.

---

## PARTIE II — Implémentation

### 3. Le simulateur / machine universelle (fourni — à compléter et tester)

Le simulateur ci-dessous joue le rôle de **U** : il prend la *description* d'une MT (états, table δ, état initial, états finaux) et un mot, puis simule. C'est volontairement un simulateur générique : changer d'« opération », c'est seulement **changer la table de transition** passée en entrée — exactement l'idée de l'universalité.

```python
def run_tm(transitions, q0, finaux, mot, blank='_', max_steps=200_000, trace=False):
    """
    Simulateur universel d'une MT déterministe mono-ruban.
    transitions : dict {(etat, symbole) : (etat', symbole', direction)}  direction ∈ {'L','R','S'}
    Retourne (accepte, ruban_final_nettoyé, nb_etapes).
    Le ruban est un dict {indice: symbole} -> ruban bi-infini, expansion implicite.
    """
    ruban = {i: c for i, c in enumerate(mot)}
    pos, etat, steps = 0, q0, 0
    while steps < max_steps:
        sym = ruban.get(pos, blank)
        if trace:
            lo = min(ruban) if ruban else 0
            hi = max(ruban) if ruban else 0
            mot_courant = ''.join(ruban.get(i, blank) for i in range(lo, hi + 1))
            print(f"[{steps:>4}] état={etat:<6} tête={pos:<3} lu='{sym}'   ruban={mot_courant!r}")
        if etat in finaux:                 # arrêt acceptant
            break
        cle = (etat, sym)
        if cle not in transitions:         # aucune transition -> arrêt (rejet)
            break
        etat, ecrit, direction = transitions[cle]
        ruban[pos] = ecrit
        if direction == 'R':   pos += 1
        elif direction == 'L': pos -= 1
        # 'S' : la tête ne bouge pas
        steps += 1
    # lecture du résultat : on retire les blancs de bord
    if not ruban:
        return etat in finaux, '', steps
    lo, hi = min(ruban), max(ruban)
    sortie = ''.join(ruban.get(i, blank) for i in range(lo, hi + 1)).strip(blank)
    return etat in finaux, sortie, steps


def n1(s):                      # nombre de '1' = valeur d'un entier unaire
    return s.count('1')
```

**Convention de codage des entiers :** un entier *n* est représenté en **unaire** par le mot `1`ⁿ (donc 0 = mot vide). Les opérandes sont séparées par un symbole d'opérateur (`+`, `-`, `*`, `/`). Le symbole blanc est `_`.

---

### 4. La calculatrice — opérations comme **vraies** machines de Turing

Chaque opération est *une table δ* exécutée par `run_tm`. **C'est la table qui « est » la machine** ; le simulateur ne fait que la lire — d'où le lien direct avec la MTU.

#### 4.1 Addition `1ⁿ + 1ᵐ → 1ⁿ⁺ᵐ`  *(table vérifiée pas-à-pas)*

```python
ADD = {
    ('q0', '1'): ('q0', '1', 'R'),   # (a) on traverse n vers la droite
    ('q0', '+'): ('q1', '1', 'R'),   # (b) le '+' devient un '1' : on a "fusionné" les deux blocs
    ('q1', '1'): ('q1', '1', 'R'),   # (c) on traverse m vers la droite
    ('q1', '_'): ('q2', '_', 'L'),   # (d) fin du mot : demi-tour
    ('q2', '1'): ('qf', '_', 'S'),   # (e) on efface le tout dernier '1' puis on accepte
}
ADD_Q0, ADD_F = 'q0', {'qf'}
```

**Idée :** `1ⁿ + 1ᵐ` contient n + 1 + m symboles « 1‑équivalents » une fois le `+` transformé en `1`. On en retire **exactement un** (le dernier) : il reste n + m. Simple et O(n + m).

#### 4.2 Soustraction tronquée `1ⁿ - 1ᵐ → 1ⁿ⁻ᵐ` (n ≥ m)  *(table vérifiée pas-à-pas)*

```python
SUB = {
    # phase 1 : aller jusqu'au '-'
    ('q0', '1'): ('q0', '1', 'R'),
    ('q0', 'X'): ('q0', 'X', 'R'),
    ('q0', '-'): ('q1', '-', 'R'),
    # phase 2 : prendre un '1' de m (le marquer X), revenir
    ('q1', '1'): ('q2', 'X', 'L'),
    ('q1', 'X'): ('q1', 'X', 'R'),
    ('q1', '_'): ('q4', '_', 'L'),   # m épuisé -> nettoyage
    ('q2', 'X'): ('q2', 'X', 'L'),
    ('q2', '-'): ('q3', '-', 'L'),
    # phase 3 : barrer un '1' de n (de droite à gauche), repartir
    ('q3', '1'): ('q0', 'X', 'R'),
    ('q3', 'X'): ('q3', 'X', 'L'),
    # phase 4 : nettoyage -> on efface X et '-', on garde les '1' restants de n
    ('q4', 'X'): ('q4', '_', 'L'),
    ('q4', '-'): ('q4', '_', 'L'),
    ('q4', '1'): ('q4', '1', 'L'),
    ('q4', '_'): ('qf', '_', 'S'),
}
SUB_Q0, SUB_F = 'q0', {'qf'}
```

**Idée :** on **apparie** un `1` de droite (dans m) avec un `1` de gauche (dans n), en les marquant `X`, jusqu'à épuisement de m ; on nettoie ensuite. Comme on barre n **de droite à gauche**, les `1` survivants sont contigus à gauche → la sortie `1ⁿ⁻ᵐ` est propre. Coût O(n·m) (allers-retours).

#### 4.3 Multiplication et division — par **composition** de machines (macro-machines)

En calculabilité, composer des MT est légitime : c'est exactement ce que fait une MTU qui enchaîne des sous-programmes. On **réutilise** ADD et SUB (déjà vérifiées) :

```python
class Calculatrice:
    """Calculatrice unaire. + et - sont de vraies MT (tables ci-dessus).
       * et / sont des MACRO-machines : enchaînement contrôlé de ADD / SUB par la MTU.
       (Voir §5 pour l'esquisse d'une table monolithique unique, laissée en extension.)"""

    def addition(self, n, m):
        _, sortie, _ = run_tm(ADD, ADD_Q0, ADD_F, '1'*n + '+' + '1'*m)
        return n1(sortie)

    def soustraction(self, n, m):           # tronquée à 0
        if m > n:
            return 0
        _, sortie, _ = run_tm(SUB, SUB_Q0, SUB_F, '1'*n + '-' + '1'*m)
        return n1(sortie)

    def multiplication(self, n, m):         # n*m = addition répétée (m fois)
        acc = 0
        for _ in range(m):                  # chaque tour : un appel RÉEL à la MT d'addition
            acc = self.addition(acc, n)
        return acc

    def division(self, n, m):               # quotient et reste par soustractions répétées
        if m == 0:
            raise ZeroDivisionError("division par zéro")
        q, reste = 0, n
        while reste >= m:                    # chaque tour : un appel RÉEL à la MT de soustraction
            reste = self.soustraction(reste, m)
            q += 1
        return q, reste

    def chainer(self, valeur_initiale, operations):
        """operations = [('+', 3), ('*', 2), ('-', 1), ('/', 2), ...]"""
        v = valeur_initiale
        for op, k in operations:
            if   op == '+': v = self.addition(v, k)
            elif op == '-': v = self.soustraction(v, k)
            elif op == '*': v = self.multiplication(v, k)
            elif op == '/': v, _ = self.division(v, k)
            else: raise ValueError(f"opérateur inconnu : {op}")
        return v
```

**Jeu de tests à fournir et faire passer :**

```python
def tests():
    c = Calculatrice()
    for n in range(7):
        for m in range(7):
            assert c.addition(n, m) == n + m
            assert c.soustraction(n, m) == max(0, n - m)
            assert c.multiplication(n, m) == n * m
            if m:
                assert c.division(n, m) == divmod(n, m)
    # chaînage : (2 + 1) * 2 - 1 = 5 ; puis / 2 = 2 (reste ignoré)
    assert c.chainer(2, [('+',1), ('*',2), ('-',1), ('/',2)]) == 2
    print("Tous les tests passent.")
tests()
```

---

## PARTIE III — Explication des tables de transition (le cœur de l'évaluation)

> Compétence évaluée : **lire et justifier une table δ ligne par ligne**, en reliant chaque ligne à une *intention algorithmique* et à un *invariant*.

### A. Grille de lecture d'une ligne `(q, a) → (q', b, d)`

Chaque ligne répond à 4 questions : **Où suis-je ?** (état q = « phase » du calcul + mémoire finie) · **Que vois-je ?** (symbole a) · **Que fais-je ?** (j'écris b, je vais en d) · **Où vais-je ?** (état q' = phase suivante). L'**état encode la mémoire finie** ; le ruban encode la mémoire illimitée.

### B. Addition — rôle de chaque état et de chaque ligne

| Ligne | Transition | Rôle / invariant |
|------|-------------|------------------|
| (a) | (q0,1)→(q0,1,R) | **q0 = « je parcours le premier opérande n »**. Invariant : tout ce qui est à gauche de la tête est définitif. |
| (b) | (q0,+)→(q1,1,R) | **Cœur de l'astuce** : le séparateur `+` devient un `1`, ce qui colle n et m en un seul bloc `1ⁿ⁺¹⁺ᵐ`. Changement de phase q0→q1. |
| (c) | (q1,1)→(q1,1,R) | **q1 = « je parcours m pour trouver la fin »**. On ne modifie rien. |
| (d) | (q1,_)→(q2,_,L) | Détection de la **fin du mot** (blanc) ; demi-tour pour corriger le « +1 » introduit en (b). |
| (e) | (q2,1)→(qf,_,S) | On efface **le dernier 1** (compense le `+`→`1`) puis acceptation. Résultat = `1ⁿ⁺ᵐ`. |

**Trace 2 + 1 :** `11+1`
`q0:11+1 → q0(R)…→ (q0,'+')` écrit 1 → `111`1 puis q1 parcourt jusqu'au blanc, q2 efface le dernier → **`111` = 3**. ✔

### C. Soustraction — lecture par **phases**

Les états ne sont pas « décoratifs » : ils nomment des **phases** d'un même algorithme d'appariement.

| État | Signification (phase) |
|------|------------------------|
| q0 | revenir/aller vers le séparateur `-` (en sautant les `1` de n et les `X` déjà posés) |
| q1 | dans m : prendre un `1` non encore consommé, le marquer `X` |
| q2 | revenir vers la gauche jusqu'au `-` |
| q3 | dans n : barrer (`X`) un `1`, **de droite à gauche** |
| q4 | nettoyage final : effacer `X` et `-`, conserver les `1` restants |

Points qui « font tomber » beaucoup d'étudiants, à expliquer explicitement dans le rapport :

- **(q0,X)→(q0,X,R)** et **(q1,X)→(q1,X,R)** : sans ces lignes, la machine se bloque dès le 2ᵉ tour, car elle re-rencontre ses propres marques `X`. *La table doit gérer ses propres traces.*
- **Direction du barrage dans n (q3, de droite à gauche)** : c'est ce choix qui garantit que les `1` survivants sont **contigus à gauche**, donc une sortie propre sans étape de compactage.
- **(q1,_)→(q4,…)** : la condition d'arrêt « m épuisé » est détectée par un **blanc**, pas par un compteur (un automate fini ne sait pas compter au-delà de ses états — c'est le ruban qui compte).

**Trace 3 − 2 :** `111-11` → appariements successifs → `XX-XX` puis nettoyage → **`1` = 1**. ✔
**Cas-limites à vérifier en soutenance :** n = m (→ 0), m = 0 (→ n), n = 0.

### D. Pourquoi `*` et `/` ne sont *pas* données comme une table unique

Un multiplicateur/diviseur **mono-ruban en un seul δ** existe mais demande ~15–20 états (copie répétée d'un bloc, marquage à double niveau, recopie/restauration, nettoyage avec délimiteur). Plutôt que de présenter une table longue **non exécutée** (donc non garantie), on en donne une **réalisation par composition** vérifiable (réutilisation de ADD/SUB) — ce qui est *aussi* une leçon : **les MT se composent**, et la MTU est précisément le mécanisme qui orchestre ces compositions.

---

## PARTIE IV — Extensions (bonus master)

1. **Table monolithique de la multiplication** `1ⁿ*1ᵐ → 1ⁿᵐ` : implémenter l'algorithme « pour chaque `1` de m (marqué `Y`), recopier `1ⁿ` dans une zone résultat délimitée par `=`, restaurer n, puis nettoyer ». Valider par `run_tm`. (≈ +4 pts)
2. **MTU « vraie »** : au lieu d'un simulateur Python générique, faire de U **elle-même une MT** dont le ruban contient l'encodage binaire ⟨M⟩##w, et la table δ_U simule un cycle. Mesurer le surcoût empirique vs. la borne O(t·|⟨M⟩|).
3. **Mesure du ralentissement** : tracer nb_étapes(U) / nb_étapes(M) en fonction de |⟨M⟩| et discuter au regard de Hennie–Stearns.
4. **Représentation binaire** plutôt qu'unaire : addition O(n) avec retenue ; comparer la taille des tables.

---

## Livrables & barème

| Élément | Détail | Points |
|--------|--------|--------|
| Rapport théorique I.1–I.5 | encodage injectif, invariant de U, surcoût **sourcé**, indécidabilité | 40 |
| Implémentation | `run_tm`, ADD, SUB (tables), Calculatrice, **tests qui passent** | 45 |
| Explication des tables (Partie III) | lecture ligne-à-ligne, phases, cas-limites, traces | 10 |
| Soutenance | démo + un cas chaîné + difficultés | 5 |
| Bonus | extensions Partie IV | +10 max |
| Honnêteté intellectuelle | toute borne de complexité démontrée **ou** référencée | gate (malus si non respecté) |

**Critères de différenciation master :** rigueur des invariants, gestion explicite des marques sur le ruban, conscience des limites (indécidabilité, surcoût), et capacité à **expliquer** plutôt qu'à seulement faire tourner.
