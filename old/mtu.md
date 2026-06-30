TP Master — MTU & calculatrice arithmétique unaire
Partie I — Théorie
Définition de la MTU. Une machine universelle U vérifie, pour toute MT M et tout mot w :

U(⟨M⟩ ## w) se comporte comme M(w) : U accepte ⟺ M accepte, et le ruban final de U code celui de M.

L'entrée de U contient donc un programme (⟨M⟩) traité comme une donnée : c'est le principe du programme enregistré, ancêtre de l'interpréteur.
Questions à rédiger (rigueur exigée) :

Encodage ⟨M⟩. Numéroter états et symboles, linéariser δ en quintuplets (q,a)→(q′,b,d). Justifier qu'il est injectif et décodable.
Invariant de simulation de U. À tout instant U maintient sur son ruban : ⟨M⟩ figé, l'état simulé, le ruban simulé, la position de tête simulée. Décrire un cycle : lire → chercher la transition dans ⟨M⟩ → écrire → déplacer → mettre à jour l'état.
Thèse de Church–Turing. L'énoncer ; rappeler que ce n'est pas un théorème ; citer ≥ 2 modèles équivalents (λ-calcul, fonctions récursives, RAM).
Surcoût de simulation (à sourcer, sans inventer de constante) : une MTU multi-ruban simule t étapes en O(t·|⟨M⟩|) ; le passage multi→mono coûte au plus un facteur quadratique ; résultat classique à citer (Hennie–Stearns) : ralentissement logarithmique atteignable. Je ne suis pas certain des constantes exactes — à vérifier dans le cours/Sipser ou Arora–Barak avant de l'écrire comme un fait.
Limites. Par réduction depuis HALT : « U s'arrête sur ⟨M⟩##w » est indécidable. L'universalité n'est pas l'omniscience.

Partie II — Le simulateur universel
pythondef run_tm(transitions, q0, finaux, mot, blank='_', max_steps=200_000, trace=False):
    """transitions : {(etat, symbole): (etat', symbole', dir∈{'L','R','S'})}
       Retourne (accepte, ruban_final_nettoyé, nb_etapes)."""
    ruban = {i: c for i, c in enumerate(mot)}
    pos, etat, steps = 0, q0, 0
    while steps < max_steps:
        sym = ruban.get(pos, blank)
        if trace:
            lo, hi = (min(ruban), max(ruban)) if ruban else (0, 0)
            courant = ''.join(ruban.get(i, blank) for i in range(lo, hi+1))
            print(f"[{steps:>4}] {etat:<6} tête={pos:<3} lu='{sym}' ruban={courant!r}")
        if etat in finaux:
            break
        cle = (etat, sym)
        if cle not in transitions:          # plus de transition -> arrêt (rejet)
            break
        etat, ecrit, d = transitions[cle]
        ruban[pos] = ecrit
        pos += 1 if d == 'R' else -1 if d == 'L' else 0
        steps += 1
    if not ruban:
        return etat in finaux, '', steps
    lo, hi = min(ruban), max(ruban)
    sortie = ''.join(ruban.get(i, blank) for i in range(lo, hi+1)).strip(blank)
    return etat in finaux, sortie, steps

def n1(s):              # valeur d'un entier unaire
    return s.count('1')
Conventions : entier n = 1ⁿ (donc 0 = mot vide) ; opérandes séparées par + - * / ; blanc = _. Changer d'opération = changer la table passée à run_tm → c'est exactement l'idée de l'universalité.
Partie II (suite) — Les opérations comme vraies MT
Addition 1ⁿ+1ᵐ → 1ⁿ⁺ᵐ (vérifiée à la main)
pythonADD = {
    ('q0','1'): ('q0','1','R'),   # (a) traverser n
    ('q0','+'): ('q1','1','R'),   # (b) le '+' devient '1' : on fusionne les deux blocs
    ('q1','1'): ('q1','1','R'),   # (c) traverser m
    ('q1','_'): ('q2','_','L'),   # (d) fin du mot -> demi-tour
    ('q2','1'): ('qf','_','S'),   # (e) effacer le dernier '1' (compense le +) puis accepter
}
ADD_Q0, ADD_F = 'q0', {'qf'}
Idée : après (b), le ruban contient n+1+m « uns » ; on en retire un seul ⇒ n+m. Coût O(n+m).
Soustraction tronquée 1ⁿ-1ᵐ → 1ⁿ⁻ᵐ, n ≥ m (vérifiée à la main)
pythonSUB = {
    ('q0','1'): ('q0','1','R'),   ('q0','X'): ('q0','X','R'),
    ('q0','-'): ('q1','-','R'),
    ('q1','1'): ('q2','X','L'),   ('q1','X'): ('q1','X','R'),
    ('q1','_'): ('q4','_','L'),   # m épuisé -> nettoyage
    ('q2','X'): ('q2','X','L'),   ('q2','-'): ('q3','-','L'),
    ('q3','1'): ('q0','X','R'),   ('q3','X'): ('q3','X','L'),
    ('q4','X'): ('q4','_','L'),   ('q4','-'): ('q4','_','L'),
    ('q4','1'): ('q4','1','L'),   ('q4','_'): ('qf','_','S'),
}
SUB_Q0, SUB_F = 'q0', {'qf'}
Idée : on apparie un 1 de m (marqué X) avec un 1 de n (barré X, de droite à gauche), jusqu'à épuiser m, puis on nettoie. Le barrage droite→gauche garantit des survivants contigus ⇒ sortie propre. Coût O(n·m).
Multiplication & division — par composition (macro-machines)
pythonclass Calculatrice:
    def addition(self, n, m):
        _, s, _ = run_tm(ADD, ADD_Q0, ADD_F, '1'*n + '+' + '1'*m); return n1(s)
    def soustraction(self, n, m):
        if m > n: return 0
        _, s, _ = run_tm(SUB, SUB_Q0, SUB_F, '1'*n + '-' + '1'*m); return n1(s)
    def multiplication(self, n, m):          # addition répétée : m appels RÉELS à la MT ADD
        acc = 0
        for _ in range(m): acc = self.addition(acc, n)
        return acc
    def division(self, n, m):                # soustractions répétées
        if m == 0: raise ZeroDivisionError
        q, r = 0, n
        while r >= m: r = self.soustraction(r, m); q += 1
        return q, r
    def chainer(self, v0, ops):              # ops = [('+',3),('*',2),('-',1),('/',2)]
        v = v0
        for op, k in ops:
            if   op=='+': v = self.addition(v, k)
            elif op=='-': v = self.soustraction(v, k)
            elif op=='*': v = self.multiplication(v, k)
            elif op=='/': v, _ = self.division(v, k)
        return v
pythondef tests():
    c = Calculatrice()
    for n in range(7):
        for m in range(7):
            assert c.addition(n,m)==n+m
            assert c.soustraction(n,m)==max(0,n-m)
            assert c.multiplication(n,m)==n*m
            if m: assert c.division(n,m)==divmod(n,m)
    assert c.chainer(2, [('+',1),('*',2),('-',1),('/',2)])==2   # (((2+1)*2)-1)//2 = 2
    print("Tous les tests passent.")
tests()
Composer des MT est légitime : c'est ce que fait une MTU qui enchaîne des sous-programmes. (Une table monolithique unique pour * reste possible — voir bonus.)
Partie III — Expliquer une table de transition (cœur de la note)
Grille de lecture de (q,a)→(q′,b,d) : où suis-je (q = phase + mémoire finie) · que vois-je (a) · que fais-je (écris b, vais en d) · où vais-je (q′). L'état encode la mémoire finie ; le ruban encode la mémoire illimitée.
Addition, ligne par ligne
LigneRôle / invariant(a) q0,1→Rq0 = « je parcours n » ; le gauche est définitif(b) q0,+→1,Rastuce centrale : +→1 colle n et m(c) q1,1→Rq1 = « je parcours m »(d) q1,_→Ldétection de fin par le blanc (pas de compteur)(e) q2,1→qf,_on retire le 1 excédentaire, on accepte
Trace 2+1 : 11+1 → q0…→ +→1 → 1111 → demi-tour → efface le dernier → 111=3 ✔
Soustraction : les états sont des phases
q0 = aller vers - (en sautant 1 et X) · q1 = prendre un 1 de m (→X) · q2 = revenir au - · q3 = barrer un 1 de n (droite→gauche) · q4 = nettoyer.
Trois pièges à expliciter dans le rapport :

(q0,X)→R et (q1,X)→R : sans eux la machine se bloque au 2ᵉ tour car elle re-rencontre ses propres marques. Une table doit gérer ses propres traces.
Barrage de n droite→gauche : c'est ce qui rend la sortie contiguë (pas de compactage).
(q1,_)→q4 : la fin de m est détectée par un blanc — un automate fini ne compte pas, c'est le ruban qui compte.

Cas-limites à montrer en soutenance : n=m→0, m=0→n, n=0.
Pourquoi * et / ne sont pas une table unique : une version mono-ruban en un seul δ demande ~15–20 états (copie répétée, double marquage, restauration, nettoyage délimité). Plutôt qu'une table longue non exécutée donc non garantie, on donne une réalisation vérifiable par composition — ce qui illustre aussi que les MT se composent, et que la MTU orchestre ces compositions.
Partie IV — Bonus master

Table monolithique de 1ⁿ*1ᵐ→1ⁿᵐ (recopie de bloc + marqueurs Y/x + zone résultat délimitée par =), validée par run_tm.
Faire de U une vraie MT (ruban = ⟨M⟩##w binaire, δ_U simule un cycle) et mesurer le surcoût empirique vs O(t·|⟨M⟩|).
Tracer étapes(U)/étapes(M) selon |⟨M⟩| et discuter au regard de Hennie–Stearns.
Variante binaire (addition O(n) avec retenue) ; comparer la taille des tables.

Barème
Théorie I.1–I.5 : 40 · Implémentation (run_tm, ADD, SUB, Calculatrice, tests qui passent) : 45 · Explication des tables (III) : 10 · Soutenance : 5 · Bonus : +10 max. Gate honnêteté : toute borne de complexité doit être démontrée ou référencée.


