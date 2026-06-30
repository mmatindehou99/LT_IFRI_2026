#!/usr/bin/env python3
"""Auto-installateur du projet « formlang ».
Usage :  python setup_projet.py            # crée tout (sans écraser l'existant)
         python setup_projet.py --force    # réécrit même si le fichier existe
         python setup_projet.py --root DIR # cible un autre dossier (défaut: .)

Écrit l'arborescence complète : formlang/, apps/, tests/, docs/ + infra.
Aucune dépendance hors stdlib. Ensuite :  pip install pytest && pytest -q
"""
import argparse
import os

MARK = "@@FILE@@ "

BUNDLE = r'''
@@FILE@@ pyproject.toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "formlang-projet"
version = "0.1.0"
requires-python = ">=3.10"

[tool.pytest.ini_options]
pythonpath = ["."]
@@FILE@@ conftest.py
# Permet à pytest d'importer formlang/ et apps/ depuis la racine.
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
@@FILE@@ .gitignore
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
.venv/
out.txt
@@FILE@@ LICENSE
Ce matériel pédagogique est placé dans le domaine public (CC0 1.0).
Dans la mesure permise par la loi, les auteurs renoncent à tous leurs droits
d'auteur et droits voisins sur ce travail. Aucune garantie n'est fournie.
@@FILE@@ Makefile
.PHONY: test demo morpho clean

test:
	pytest -q

demo:
	python pipeline.py

morpho:
	python pipeline.py --morpho mufafak

clean:
	rm -rf __pycache__ .pytest_cache **/__pycache__ *.egg-info out.txt
@@FILE@@ formlang/__init__.py
"""formlang — bibliothèque pédagogique : du régulier à l'universel.
Couches : dfa/nfa (régulier), fst (rationnel), pda/cfg (hors-contexte),
tree (arbres réguliers), turing/utm (récursivement énumérable)."""

from .tree import Term, TreeAutomaton, product, REJECT
from .turing import TuringMachine, TMResult
from .utm import UniversalTM, encode, decode

__all__ = [
    "Term", "TreeAutomaton", "product", "REJECT",
    "TuringMachine", "TMResult",
    "UniversalTM", "encode", "decode",
]
@@FILE@@ formlang/tree.py
"""Automate d'arbres ASCENDANT déterministe (Bottom-Up Tree Automaton).

A = (Q, F, Delta) sur un alphabet GRADUÉ implicite : un symbole peut apparaître
avec différentes arités, distinguées par le nombre d'enfants dans Delta.

C'est le coeur réutilisé par apps/morpho (morphologie) ET apps/shield
(AttackDecomposer) : seules changent les règles Delta. Une application ne doit
JAMAIS redéfinir un automate — elle instancie celui-ci.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Hashable
from collections import defaultdict


@dataclass(frozen=True)
class Term:
    """Terme t ::= symbol(child1, ..., childk).  label = texte d'une feuille
    (utile en morphologie) ; il est IGNORÉ par l'automate (Delta n'agit que sur
    le symbole et les états des enfants)."""
    symbol: str
    children: tuple["Term", ...] = ()
    label: Optional[str] = None


class _Reject:
    __slots__ = ()
    def __repr__(self):
        return "REJECT"


REJECT = _Reject()   # sentinelle d'état « aucune règle applicable »


class TreeAutomaton:
    def __init__(self, final_states):
        # Delta : (symbol, tuple(états des enfants)) -> état résultat
        self.delta: dict[tuple[str, tuple], Hashable] = {}
        self.final: set = set(final_states)

    def add_rule(self, symbol: str, child_states, result) -> None:
        self.delta[(symbol, tuple(child_states))] = result

    def run(self, t: Term):
        """Étiquetage post-ordre (feuilles -> racine). Renvoie l'état de la
        racine ou REJECT si une règle manque quelque part. Coût O(|t|)."""
        child_states = []
        for c in t.children:
            s = self.run(c)
            if s is REJECT:
                return REJECT
            child_states.append(s)
        return self.delta.get((t.symbol, tuple(child_states)), REJECT)

    def accepts(self, t: Term) -> bool:
        return self.run(t) in self.final


def product(a1: TreeAutomaton, a2: TreeAutomaton) -> TreeAutomaton:
    """Automate produit : L(product) = L(a1) ∩ L(a2). États = paires (q1, q2).
    Clôture par intersection des langages d'arbres réguliers."""
    P = TreeAutomaton({(f1, f2) for f1 in a1.final for f2 in a2.final})
    by_key1, by_key2 = defaultdict(list), defaultdict(list)
    for (sym, kids), res in a1.delta.items():
        by_key1[(sym, len(kids))].append((kids, res))
    for (sym, kids), res in a2.delta.items():
        by_key2[(sym, len(kids))].append((kids, res))
    for key, rules1 in by_key1.items():
        for k1, r1 in rules1:
            for k2, r2 in by_key2.get(key, ()):
                paired = tuple(zip(k1, k2))     # enfants = paires d'états
                P.add_rule(key[0], paired, (r1, r2))
    return P
@@FILE@@ formlang/turing.py
"""Machine de Turing déterministe, mono-ruban, ruban bi-infini (dict).
delta : (état, symbole) -> (état', symbole', direction ∈ {'L','R','S'})."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TMResult:
    accepted: bool
    tape: str            # ruban final, blancs de bord retirés
    steps: int
    trace: list = field(default_factory=list)


@dataclass
class TuringMachine:
    transitions: dict           # (q, a) -> (q', b, d)
    start: str
    accept: set
    blank: str = "_"
    reject: set = field(default_factory=set)

    def _read(self, tape: dict) -> str:
        if not tape:
            return ""
        lo, hi = min(tape), max(tape)
        s = "".join(tape.get(i, self.blank) for i in range(lo, hi + 1))
        return s.strip(self.blank)

    def _window(self, tape: dict) -> str:
        if not tape:
            return ""
        lo, hi = min(tape), max(tape)
        return "".join(tape.get(i, self.blank) for i in range(lo, hi + 1))

    def run(self, word: str, max_steps: int = 1_000_000, trace: bool = False) -> TMResult:
        tape = {i: c for i, c in enumerate(word)}
        pos, state, steps = 0, self.start, 0
        hist = []
        while steps < max_steps:
            sym = tape.get(pos, self.blank)
            if trace:
                hist.append((steps, state, pos, self._window(tape)))
            if state in self.accept:
                return TMResult(True, self._read(tape), steps, hist)
            if state in self.reject:
                return TMResult(False, self._read(tape), steps, hist)
            key = (state, sym)
            if key not in self.transitions:           # arrêt : aucune transition
                return TMResult(state in self.accept, self._read(tape), steps, hist)
            state, write, d = self.transitions[key]
            tape[pos] = write
            pos += 1 if d == "R" else -1 if d == "L" else 0
            steps += 1
        raise RuntimeError("max_steps dépassé — boucle infinie suspectée")
@@FILE@@ formlang/utm.py
"""Machine de Turing universelle.
U(<M> ## w) : on ENCODE M en une chaîne (donnée), puis U la DÉCODE et simule M
sur w. C'est tout le principe du programme enregistré / de l'interpréteur."""
from __future__ import annotations
import json
from .turing import TuringMachine, TMResult


def encode(machine: TuringMachine) -> str:
    """Linéarisation injective de M en JSON : <M>."""
    return json.dumps({
        "start": machine.start,
        "accept": sorted(machine.accept),
        "blank": machine.blank,
        "transitions": [[q, a, q2, b, d]
                        for (q, a), (q2, b, d) in machine.transitions.items()],
    }, sort_keys=True)


def decode(desc: str) -> TuringMachine:
    """Reconstruit M à partir de <M> (décodabilité)."""
    d = json.loads(desc)
    trans = {(q, a): (q2, b, dd) for q, a, q2, b, dd in d["transitions"]}
    return TuringMachine(trans, d["start"], set(d["accept"]), d.get("blank", "_"))


class UniversalTM:
    def run(self, encoded_machine: str, word: str, **kw) -> TMResult:
        """U lit la description encodée, la décode, puis simule sur w."""
        return decode(encoded_machine).run(word, **kw)
@@FILE@@ formlang/dfa.py
"""Automate fini déterministe. run/accepts + minimisation par raffinement de
partition (Moore). Un mot est un arbre dégénéré (branche unaire) : ce module est
l'étage le plus bas de la hiérarchie."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque


@dataclass
class DFA:
    transitions: dict            # (state, sym) -> state
    start: str
    accept: set
    alphabet: set = field(default_factory=set)

    def __post_init__(self):
        if not self.alphabet:
            self.alphabet = {a for (_, a) in self.transitions}

    def run(self, w: str):
        s = self.start
        for c in w:
            if (s, c) not in self.transitions:
                return None                      # transition manquante -> rejet
            s = self.transitions[(s, c)]
        return s

    def accepts(self, w: str) -> bool:
        return self.run(w) in self.accept

    def _reachable(self) -> set:
        seen, todo = {self.start}, deque([self.start])
        while todo:
            s = todo.popleft()
            for a in self.alphabet:
                t = self.transitions.get((s, a))
                if t is not None and t not in seen:
                    seen.add(t)
                    todo.append(t)
        return seen

    def _completed(self):
        """Complète l'AFD avec un puits si nécessaire (requis par Moore)."""
        SINK = "__sink__"
        trans = dict(self.transitions)
        states = self._reachable()
        need_sink = False
        for s in states:
            for a in self.alphabet:
                if (s, a) not in trans:
                    trans[(s, a)] = SINK
                    need_sink = True
        if need_sink:
            states = states | {SINK}
            for a in self.alphabet:
                trans[(SINK, a)] = SINK
        return states, trans

    def minimize(self) -> "DFA":
        states, trans = self._completed()
        acc = {s for s in states if s in self.accept}
        block = {s: (0 if s in acc else 1) for s in states}
        alpha = sorted(self.alphabet)
        while True:
            sig = {}
            for s in states:
                sig[s] = (block[s], tuple(block[trans[(s, a)]] for a in alpha))
            groups = {}
            for s in states:
                groups.setdefault(sig[s], []).append(s)
            new_block = {}
            for i, (_, members) in enumerate(sorted(groups.items())):
                for s in members:
                    new_block[s] = i
            if new_block == block:
                break
            block = new_block
        rep = {}
        for s in states:
            rep.setdefault(block[s], s)
        new_trans = {}
        for b, r in rep.items():
            for a in alpha:
                new_trans[(f"q{b}", a)] = f"q{block[trans[(r, a)]]}"
        new_accept = {f"q{block[s]}" for s in acc}
        return DFA(new_trans, f"q{block[self.start]}", new_accept, set(self.alphabet))

    def num_states(self) -> int:
        st = {self.start}
        for (s, _), t in self.transitions.items():
            st.add(s)
            st.add(t)
        return len(st)
@@FILE@@ formlang/nfa.py
"""Automate fini non déterministe (avec ε noté ''). Déterminisation par
construction des sous-ensembles -> DFA."""
from __future__ import annotations
from dataclasses import dataclass, field
from .dfa import DFA


@dataclass
class NFA:
    transitions: dict            # (state, sym|'') -> set(states)
    start: str
    accept: set
    alphabet: set = field(default_factory=set)

    def __post_init__(self):
        if not self.alphabet:
            self.alphabet = {a for (_, a) in self.transitions if a != ""}

    def _eps_closure(self, states: frozenset) -> frozenset:
        stack, clos = list(states), set(states)
        while stack:
            s = stack.pop()
            for t in self.transitions.get((s, ""), ()):
                if t not in clos:
                    clos.add(t)
                    stack.append(t)
        return frozenset(clos)

    def _move(self, states: frozenset, a: str) -> frozenset:
        out = set()
        for s in states:
            out |= self.transitions.get((s, a), set())
        return frozenset(out)

    def accepts(self, w: str) -> bool:
        cur = self._eps_closure(frozenset({self.start}))
        for c in w:
            cur = self._eps_closure(self._move(cur, c))
        return any(s in self.accept for s in cur)

    def to_dfa(self) -> DFA:
        start = self._eps_closure(frozenset({self.start}))
        name = {start: "S0"}
        trans, todo, n = {}, [start], 1
        while todo:
            cur = todo.pop()
            for a in sorted(self.alphabet):
                nxt = self._eps_closure(self._move(cur, a))
                if not nxt:
                    continue
                if nxt not in name:
                    name[nxt] = f"S{n}"
                    n += 1
                    todo.append(nxt)
                trans[(name[cur], a)] = name[nxt]
        accept = {name[st] for st in name if any(s in self.accept for s in st)}
        return DFA(trans, name[start], accept, set(self.alphabet))
@@FILE@@ formlang/fst.py
"""Transducteur fini séquentiel (one-way), lettre à lettre : une entrée -> une
sortie. Suffisant pour la normalisation (leet). Le MIROIR w -> w^R N'EST PAS
réalisable one-way (mémoire bornée) : il faudrait un transducteur bidirectionnel
-> voir reverse_twoway()."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SequentialFST:
    transitions: dict            # (state, in_sym) -> (next_state, out_sym)
    start: str
    finals: set
    identity_on_missing: bool = False   # émettre le symbole inchangé si absent

    def transduce(self, w: str) -> str:
        s, out = self.start, []
        for c in w:
            if (s, c) in self.transitions:
                s, o = self.transitions[(s, c)]
                out.append(o)
            elif self.identity_on_missing:
                out.append(c)                # boucle identité, état inchangé
            else:
                raise ValueError(f"transition manquante: ({s!r},{c!r})")
        return "".join(out)


def compose(t1: SequentialFST, t2: SequentialFST) -> SequentialFST:
    """t = t2 ∘ t1 : t(w) = t2(t1(w)). Tables EXPLICITES requises (pas
    d'identity_on_missing). États = paires (s1, s2)."""
    trans = {}
    for (s1, a), (s1n, b) in t1.transitions.items():
        for (s2, x), (s2n, c) in t2.transitions.items():
            if x == b:
                trans[((s1, s2), a)] = ((s1n, s2n), c)
    finals = {(f1, f2) for f1 in t1.finals for f2 in t2.finals}
    return SequentialFST(trans, (t1.start, t2.start), finals)


def leet_fst() -> SequentialFST:
    """4->a 3->e 0->o 1->i 5->s ; identité sinon. Un seul état q0 (final)."""
    leet = {"4": "a", "3": "e", "0": "o", "1": "i", "5": "s"}
    trans = {("q0", k): ("q0", v) for k, v in leet.items()}
    return SequentialFST(trans, "q0", {"q0"}, identity_on_missing=True)


def reverse_twoway(w: str) -> str:
    """Le renversement modélisé comme une transduction BIDIRECTIONNELLE
    (lecture jusqu'au bout puis émission de droite à gauche)."""
    return w[::-1]
@@FILE@@ formlang/pda.py
"""Automate à pile déterministe pour délimiteurs imbriqués (langage de Dyck
multi-types + symboles ignorés). Acceptation par PILE VIDE."""
from __future__ import annotations


class DelimiterPDA:
    def __init__(self, pairs=(("[", "]"), ("(", ")")), ignore=("a", "o", "r", "e")):
        self.open = {o for o, _ in pairs}
        self.match = {c: o for o, c in pairs}     # fermant -> ouvrant attendu
        self.ignore = set(ignore)

    def accepts(self, w: str) -> bool:
        stack = []
        for c in w:
            if c in self.open:                    # empiler témoin
                stack.append(c)
            elif c in self.match:                 # dépiler si sommet correspond
                if not stack or stack[-1] != self.match[c]:
                    return False
                stack.pop()
            elif c in self.ignore:                # pile inchangée
                continue
            else:
                return False                      # symbole hors alphabet
        return len(stack) == 0                    # acceptation : pile vide
@@FILE@@ formlang/cfg.py
"""Grammaire hors-contexte minimale : génération bornée des mots dérivables
jusqu'à une longueur donnée (utile pour vérifier qu'une grammaire engendre bien
un langage). La reconnaissance générale (CYK) est laissée en extension."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CFG:
    rules: dict             # non-terminal -> liste de productions (tuples de symboles)
    start: str
    nonterminals: set

    def generate(self, max_len: int) -> set:
        """Mots terminaux dérivables, de longueur <= max_len (BFS sur les formes
        sententielles, élagué par la longueur des terminaux déjà produits)."""
        out, seen = set(), set()
        todo = [(self.start,)]
        while todo:
            form = todo.pop()
            if form in seen:
                continue
            seen.add(form)
            term_len = sum(1 for s in form if s not in self.nonterminals)
            if term_len > max_len:
                continue
            idx = next((i for i, s in enumerate(form) if s in self.nonterminals), None)
            if idx is None:
                out.add("".join(form))
                continue
            nt = form[idx]
            for prod in self.rules.get(nt, ()):
                new = form[:idx] + tuple(prod) + form[idx + 1:]
                if sum(1 for s in new if s not in self.nonterminals) <= max_len:
                    todo.append(new)
        return out


def balanced_cfg() -> CFG:
    """S -> S S | [ S ] | ( S ) | a | o | r | ε  (prompts bien parenthésés)."""
    return CFG(
        rules={"S": [("S", "S"), ("[", "S", "]"), ("(", "S", ")"),
                     ("a",), ("o",), ("r",), ()]},
        start="S", nonterminals={"S"},
    )
@@FILE@@ formlang/myhill_nerode.py
"""Congruence de Myhill-Nerode (sur les mots) : u ~ v ssi pour tout suffixe s,
(u s ∈ L) <=> (v s ∈ L). On l'approxime sur un ensemble FINI de suffixes témoins
pour relier le nombre de classes au nombre d'états de l'AFD minimal."""
from __future__ import annotations


def nerode_classes(accepts, words, suffixes):
    """Regroupe `words` par signature (acceptation de w+s pour s dans suffixes).
    Renvoie {signature: [mots...]}. Le nombre de classes minore le nombre d'états
    de l'AFD minimal (et l'égale si les suffixes sont distinguants)."""
    classes = {}
    for w in words:
        sig = tuple(accepts(w + s) for s in suffixes)
        classes.setdefault(sig, []).append(w)
    return classes


def equivalent(u, v, accepts, suffixes) -> bool:
    return all(accepts(u + s) == accepts(v + s) for s in suffixes)
@@FILE@@ apps/__init__.py
@@FILE@@ apps/calc/__init__.py
@@FILE@@ apps/morpho/__init__.py
@@FILE@@ apps/shield/__init__.py
@@FILE@@ apps/calc/machines.py
"""Addition et soustraction unaires comme machines de Turing.
Tables tracées à la main (voir docs) ; à confirmer par tests/test_calc.py."""
from formlang.turing import TuringMachine

# ADD : 1^n + 1^m  ->  1^(n+m)
#   le '+' devient '1' (fusion des deux blocs), puis on efface UN '1' final.
ADD = TuringMachine(
    transitions={
        ("q0", "1"): ("q0", "1", "R"),
        ("q0", "+"): ("q1", "1", "R"),
        ("q1", "1"): ("q1", "1", "R"),
        ("q1", "_"): ("q2", "_", "L"),
        ("q2", "1"): ("qf", "_", "S"),
    },
    start="q0", accept={"qf"},
)

# SUB : 1^n - 1^m  ->  1^(n-m)  (tronquée, hypothèse n >= m)
#   on apparie un '1' de m (marqué X) avec un '1' de n (barré X, de droite à
#   gauche) ; quand m est épuisé, on nettoie X et '-', les '1' survivants de n
#   sont contigus à gauche -> sortie propre.
SUB = TuringMachine(
    transitions={
        ("q0", "1"): ("q0", "1", "R"), ("q0", "X"): ("q0", "X", "R"),
        ("q0", "-"): ("q1", "-", "R"),
        ("q1", "1"): ("q2", "X", "L"), ("q1", "X"): ("q1", "X", "R"),
        ("q1", "_"): ("q4", "_", "L"),
        ("q2", "X"): ("q2", "X", "L"), ("q2", "-"): ("q3", "-", "L"),
        ("q3", "1"): ("q0", "X", "R"), ("q3", "X"): ("q3", "X", "L"),
        ("q4", "X"): ("q4", "_", "L"), ("q4", "-"): ("q4", "_", "L"),
        ("q4", "1"): ("q4", "1", "L"), ("q4", "_"): ("qf", "_", "S"),
    },
    start="q0", accept={"qf"},
)
@@FILE@@ apps/calc/calculator.py
"""Calculatrice unaire. + et - sont de VRAIES MT (machines.py).
* et / sont des MACRO-machines : enchaînement contrôlé de ADD/SUB (les MT se
composent — c'est ce que fait une MTU qui orchestre des sous-machines)."""
from .machines import ADD, SUB


def _ones(s: str) -> int:
    return s.count("1")


class Calculatrice:
    def addition(self, n: int, m: int) -> int:
        return _ones(ADD.run("1" * n + "+" + "1" * m).tape)

    def soustraction(self, n: int, m: int) -> int:      # tronquée à 0
        if m > n:
            return 0
        return _ones(SUB.run("1" * n + "-" + "1" * m).tape)

    def multiplication(self, n: int, m: int) -> int:    # addition répétée
        acc = 0
        for _ in range(m):
            acc = self.addition(acc, n)
        return acc

    def division(self, n: int, m: int) -> tuple[int, int]:   # (quotient, reste)
        if m == 0:
            raise ZeroDivisionError("division par zéro")
        q, r = 0, n
        while r >= m:
            r = self.soustraction(r, m)
            q += 1
        return q, r

    def chainer(self, v0: int, ops: list[tuple[str, int]]) -> int:
        v = v0
        for op, k in ops:
            if op == "+":
                v = self.addition(v, k)
            elif op == "-":
                v = self.soustraction(v, k)
            elif op == "*":
                v = self.multiplication(v, k)
            elif op == "/":
                v, _ = self.division(v, k)
            else:
                raise ValueError(f"opérateur inconnu : {op!r}")
        return v
@@FILE@@ apps/morpho/automaton.py
"""Automate morphologique : prefix* root suffix*  (réutilise formlang.tree).
Classes : BARE / PREFIXED / SUFFIXED / CIRCUMFIXED."""
from formlang.tree import Term, TreeAutomaton


def prefix(s):
    return Term("prefix", label=s)


def root(s):
    return Term("root", label=s)


def suffix(s):
    return Term("suffix", label=s)


def nil():
    return Term("nil")


def prefixes(h, t):
    return Term("prefixes", (h, t))


def suffixes(h, t):
    return Term("suffixes", (h, t))


def rest(r, s):
    return Term("rest", (r, s))


def word(p, r):
    return Term("word", (p, r))


def build_word(pres, root_str, sufs) -> Term:
    pc = nil()
    for p in reversed(pres):
        pc = prefixes(prefix(p), pc)
    sc = nil()
    for s in reversed(sufs):
        sc = suffixes(suffix(s), sc)
    return word(pc, rest(root(root_str), sc))


def morpho_automaton() -> TreeAutomaton:
    A = TreeAutomaton(final_states={"WORD"})
    # feuilles
    A.add_rule("prefix", (), "PRE")
    A.add_rule("root",   (), "ROOT")
    A.add_rule("suffix", (), "SUF")
    A.add_rule("nil",    (), "NIL")
    # chaînes
    A.add_rule("suffixes", ("SUF", "SUFS"), "SUFS")
    A.add_rule("suffixes", ("SUF", "NIL"),  "SUFS")
    A.add_rule("prefixes", ("PRE", "PREFS"), "PREFS")
    A.add_rule("prefixes", ("PRE", "NIL"),   "PREFS")
    # rest = racine + suffixes
    A.add_rule("rest", ("ROOT", "SUFS"), "REST")
    A.add_rule("rest", ("ROOT", "NIL"),  "REST")
    # word = préfixes + rest
    A.add_rule("word", ("PREFS", "REST"), "WORD")
    A.add_rule("word", ("NIL",   "REST"), "WORD")
    return A


def _contains(t: Term, sym: str) -> bool:
    if t.symbol == sym:
        return True
    return any(_contains(c, sym) for c in t.children)


def classify(A: TreeAutomaton, t: Term) -> str:
    if not A.accepts(t):
        return "INVALID"
    p, s = _contains(t, "prefix"), _contains(t, "suffix")
    if p and s:
        return "CIRCUMFIXED"
    if s:
        return "SUFFIXED"
    if p:
        return "PREFIXED"
    return "BARE"
@@FILE@@ apps/morpho/discover.py
"""De la SURFACE à l'ARBRE : découverte d'affixes par alternance avec ∅ (idée
de Z. Harris, 1955), segmentation gloutonne, puis l'arbre est VALIDÉ et CLASSÉ
par l'automate morphologique (apps/morpho/automaton.py)."""
from __future__ import annotations
from apps.morpho.automaton import build_word


def discover(vocab: set, prefix_side: bool, K: int = 3, maxn: int = 3) -> set:
    """Un affixe est retenu s'il alterne avec ∅ sur >= K racines attestées."""
    alt: dict[str, set] = {}
    for w in vocab:
        for n in range(1, maxn + 1):
            if len(w) <= n + 1:
                continue
            affix = w[:n] if prefix_side else w[-n:]
            stem = w[n:] if prefix_side else w[:-n]
            if stem in vocab:
                alt.setdefault(affix, set()).add(stem)
    return {a for a, roots in alt.items() if len(roots) >= K}


def segment_to_tree(w: str, PRE: set, SUF: set, maxn: int = 3):
    pres = []
    changed = True
    while changed:
        changed = False
        for n in range(maxn, 0, -1):
            if len(w) > n + 1 and w[:n] in PRE:
                pres.append(w[:n])
                w = w[n:]
                changed = True
                break
    rev = []
    changed = True
    while changed:
        changed = False
        for n in range(maxn, 0, -1):
            if len(w) > n + 1 and w[-n:] in SUF:
                rev.append(w[-n:])
                w = w[:-n]
                changed = True
                break
    sufs = list(reversed(rev))
    return build_word(pres, w, sufs)
@@FILE@@ apps/morpho/corpora.py
"""Génère deux mini-corpus déterministes : langue A préfixante, langue B
suffixante. Chaque racine apparaît nue + sous toutes ses formes affixées."""
PREFIXES_A = ["mu", "ba", "ki", "vi", "li", "ma", "wa", "tu"]
SUFFIXES_B = ["lar", "ler", "im", "in", "de", "den", "si", "ya"]
CONS = "fghjzcdnrs"     # initiales disjointes des préfixes ; finale 'k' fixe
VOW = "aeiou"


def roots(n: int):
    out = []
    for c1 in CONS:
        for v1 in VOW:
            for c2 in CONS:
                for v2 in VOW:
                    out.append(c1 + v1 + c2 + v2 + "k")
                    if len(out) >= n:
                        return out
    return out


def corpus_A(n_roots: int = 150) -> list:
    A = []
    for r in roots(n_roots):
        A.append(r)
        A += [p + r for p in PREFIXES_A]
    return A


def corpus_B(n_roots: int = 150) -> list:
    B = []
    for r in roots(n_roots):
        B.append(r)
        B += [r + s for s in SUFFIXES_B]
    return B
@@FILE@@ apps/shield/detector.py
"""SingularityDetector : reconnaît les mots contenant le facteur 'or'
(annulation immédiatement suivie d'une réassignation de rôle)."""
from formlang.dfa import DFA

#  A=init, B='o' vu (armé), C=accepté (absorbant)
_DFA_OR = DFA(
    transitions={
        ("A", "a"): "A", ("A", "o"): "B", ("A", "r"): "A",
        ("B", "a"): "A", ("B", "o"): "B", ("B", "r"): "C",
        ("C", "a"): "C", ("C", "o"): "C", ("C", "r"): "C",
    },
    start="A", accept={"C"}, alphabet={"a", "o", "r"},
)


def contains_or(w: str) -> bool:
    return _DFA_OR.accepts(w)


def detector_dfa() -> DFA:
    return _DFA_OR
@@FILE@@ apps/shield/normalizer.py
"""EnhancedNormalizer : normalisation leet (lettre à lettre) + miroir (two-way)."""
from formlang.fst import leet_fst, reverse_twoway

_LEET = leet_fst()


def leet_normalize(w: str) -> str:
    return _LEET.transduce(w)


def reverse(w: str) -> str:
    return reverse_twoway(w)
@@FILE@@ apps/shield/delimiters.py
"""Détection des délimiteurs [] () bien imbriqués (automate à pile)."""
from formlang.pda import DelimiterPDA

_PDA = DelimiterPDA()


def well_parenthesized(w: str) -> bool:
    return _PDA.accepts(w)
@@FILE@@ apps/shield/decomposer.py
"""AttackDecomposer : automate d'arbres défensif, 100% structurel.
Jetons abstraits : txt, enc, ovr, role ; nœuds seq(2), frame(1), sys(1).
États : safe < ovr < role < danger. Bloqué ssi la racine est 'danger'."""
from formlang.tree import Term, TreeAutomaton

SAFE, OVR, ROLE, DANGER = "safe", "ovr", "role", "danger"
_SEV = {SAFE: 0, OVR: 1, ROLE: 2}
_BY_SEV = {0: SAFE, 1: OVR, 2: ROLE}
_ALL = (SAFE, OVR, ROLE, DANGER)


def _seq(x, y):
    if x == DANGER or y == DANGER:      # S1-S2 : le danger remonte
        return DANGER
    if {x, y} == {OVR, ROLE}:           # S3-S4 : annulation + rôle
        return DANGER
    return _BY_SEV[max(_SEV[x], _SEV[y])]   # S5 : sévérité max


def shield_automaton() -> TreeAutomaton:
    A = TreeAutomaton(final_states={DANGER})
    # feuilles (F1-F4)
    A.add_rule("txt",  (), SAFE)
    A.add_rule("enc",  (), SAFE)
    A.add_rule("ovr",  (), OVR)
    A.add_rule("role", (), ROLE)
    # seq : table complète sur 4x4 états
    for x in _ALL:
        for y in _ALL:
            A.add_rule("seq", (x, y), _seq(x, y))
    # frame / sys : un contenu non-safe dans une fiction / un faux bloc -> danger
    for x in _ALL:
        A.add_rule("frame", (x,), SAFE if x == SAFE else DANGER)
        A.add_rule("sys",   (x,), SAFE if x == SAFE else DANGER)
    return A


def txt():
    return Term("txt")


def enc():
    return Term("enc")


def ovr():
    return Term("ovr")


def role():
    return Term("role")


def seq(a, b):
    return Term("seq", (a, b))


def frame(a):
    return Term("frame", (a,))


def sys(a):
    return Term("sys", (a,))


def is_blocked(A: TreeAutomaton, t: Term) -> bool:
    return A.accepts(t)
@@FILE@@ pipeline.py
"""Pipeline intégrateur : montre les couches de formlang à l'œuvre.
- mode --word   : normalise (FST) -> détecte 'or' (AFD) -> délimiteurs (PDA)
- mode --morpho : segmente puis CLASSE un mot (BUTA morphologique)
- démo --shield : évalue quelques termes via l'AttackDecomposer (BUTA)
"""
from __future__ import annotations
import argparse

from apps.shield.normalizer import leet_normalize
from apps.shield.detector import contains_or
from apps.shield.delimiters import well_parenthesized
from apps.morpho.automaton import morpho_automaton, classify
from apps.morpho.discover import discover, segment_to_tree
from apps.shield.decomposer import (
    shield_automaton, is_blocked, txt, ovr, role, seq, frame, sys,
)


def analyze_word(raw: str) -> dict:
    norm = leet_normalize(raw)
    return {
        "entrée": raw,
        "normalisé(FST)": norm,
        "facteur_or(AFD)": contains_or(norm),
        "délimiteurs_ok(PDA)": well_parenthesized(norm),
    }


def analyze_morpho(word: str, vocab: set) -> dict:
    PRE = discover(vocab, prefix_side=True)
    SUF = discover(vocab, prefix_side=False)
    A = morpho_automaton()
    t = segment_to_tree(word, PRE, SUF)
    return {"mot": word, "classe(BUTA)": classify(A, t)}


def demo_shield() -> list:
    A = shield_automaton()
    cases = {
        "seq(txt,txt)": seq(txt(), txt()),
        "role (isolé)": role(),
        "sys(role)": sys(role()),
        "seq(frame(ovr),txt)": seq(frame(ovr()), txt()),
        "sys(seq(txt,frame(role)))": sys(seq(txt(), frame(role()))),
    }
    return [(name, is_blocked(A, t)) for name, t in cases.items()]


def main(argv=None):
    p = argparse.ArgumentParser(description="Pipeline formlang (du régulier à l'arbre)")
    p.add_argument("--word", help="mot à analyser (couches régulier/HC)")
    p.add_argument("--morpho", help="mot à classer morphologiquement")
    args = p.parse_args(argv)

    if args.word:
        for k, v in analyze_word(args.word).items():
            print(f"{k:>22} : {v}")
    if args.morpho:
        from apps.morpho.corpora import corpus_B
        res = analyze_morpho(args.morpho, set(corpus_B()))
        print(res)
    if not args.word and not args.morpho:
        print("== démo Shield (AttackDecomposer) ==")
        for name, blocked in demo_shield():
            print(f"  {'BLOQUÉ ' if blocked else 'OK     '} {name}")


if __name__ == "__main__":
    main()
@@FILE@@ tests/test_calc.py
from apps.calc.calculator import Calculatrice
from apps.calc.machines import ADD, SUB


def test_add_sub_machines_directes():
    assert ADD.run("111+11").tape.count("1") == 5
    assert SUB.run("111-11").tape.count("1") == 1
    assert SUB.run("11-11").tape == ""          # 2-2 = 0


def test_calculatrice_exhaustif():
    c = Calculatrice()
    for n in range(7):
        for m in range(7):
            assert c.addition(n, m) == n + m
            assert c.soustraction(n, m) == max(0, n - m)
            assert c.multiplication(n, m) == n * m
            if m:
                assert c.division(n, m) == divmod(n, m)


def test_chainage():
    c = Calculatrice()
    # (((2+1)*2)-1)//2 = 2
    assert c.chainer(2, [("+", 1), ("*", 2), ("-", 1), ("/", 2)]) == 2


def test_division_par_zero():
    import pytest
    with pytest.raises(ZeroDivisionError):
        Calculatrice().division(3, 0)
@@FILE@@ tests/test_turing.py
from apps.calc.machines import ADD
from formlang.utm import UniversalTM, encode, decode


def test_round_trip_encodage():
    M2 = decode(encode(ADD))
    assert M2.run("11+1").tape.count("1") == 3


def test_utm_simule_comme_la_machine():
    desc = encode(ADD)
    U = UniversalTM()
    res_direct = ADD.run("111+11")
    res_utm = U.run(desc, "111+11")
    assert res_utm.tape == res_direct.tape       # U(<M>##w) == M(w)
    assert res_utm.accepted == res_direct.accepted


def test_trace_disponible():
    res = ADD.run("1+1", trace=True)
    assert res.trace and res.trace[0][1] == "q0"
@@FILE@@ tests/test_tree.py
from formlang.tree import Term, product
from apps.morpho.automaton import morpho_automaton, build_word, classify
from apps.shield.decomposer import (
    shield_automaton, is_blocked, txt, enc, ovr, role, seq, frame, sys,
)


def test_morpho_accept_et_classes():
    A = morpho_automaton()
    assert classify(A, build_word([], "livre", []))            == "BARE"
    assert classify(A, build_word([], "jou", ["er"]))          == "SUFFIXED"
    assert classify(A, build_word(["na"], "penda", []))        == "PREFIXED"
    assert classify(A, build_word(["a", "na"], "pend", ["a"])) == "CIRCUMFIXED"


def test_morpho_rejet():
    A = morpho_automaton()
    bad = Term("word", (Term("nil"),
                        Term("rest", (Term("suffix", label="er"), Term("nil")))))
    assert classify(A, bad) == "INVALID"


def test_shield_blocage():
    A = shield_automaton()
    assert is_blocked(A, seq(txt(), txt()))               is False
    assert is_blocked(A, role())                          is False  # rôle isolé OK
    assert is_blocked(A, sys(role()))                     is True
    assert is_blocked(A, seq(frame(ovr()), txt()))        is True
    assert is_blocked(A, sys(seq(txt(), frame(role()))))  is True
    assert is_blocked(A, seq(ovr(), role()))              is True   # annulation + rôle


def _parite():
    from formlang.tree import TreeAutomaton
    A = TreeAutomaton(final_states={0})
    A.add_rule("a", (), 1)
    A.add_rule("b", (), 0)
    for x in (0, 1):
        for y in (0, 1):
            A.add_rule("c", (x, y), (x + y) % 2)
    return A


def _aumoins_un_a():
    from formlang.tree import TreeAutomaton
    A = TreeAutomaton(final_states={"yes"})
    A.add_rule("a", (), "yes")
    A.add_rule("b", (), "no")
    for x in ("yes", "no"):
        for y in ("yes", "no"):
            A.add_rule("c", (x, y), "yes" if "yes" in (x, y) else "no")
    return A


def test_produit_intersection():
    P = product(_parite(), _aumoins_un_a())
    c_aa = Term("c", (Term("a"), Term("a")))   # 2 'a' : pair ET >=1 'a'
    c_ab = Term("c", (Term("a"), Term("b")))   # 1 'a' : impair -> exclu
    assert P.accepts(c_aa) is True
    assert P.accepts(c_ab) is False
@@FILE@@ tests/test_regular.py
from formlang.fst import SequentialFST, compose
from apps.shield.detector import contains_or, detector_dfa
from apps.shield.normalizer import leet_normalize, reverse
from apps.shield.delimiters import well_parenthesized
from formlang.nfa import NFA


def test_detector_or():
    assert contains_or("aor") is True
    assert contains_or("ora") is True
    assert contains_or("aoa") is False
    assert contains_or("") is False
    assert contains_or("oar") is False


def test_minimisation_3_etats():
    assert detector_dfa().minimize().num_states() == 3


def test_nfa_to_dfa_equivalence():
    nfa = NFA(
        transitions={("q0", "a"): {"q0"}, ("q0", "b"): {"q0", "q1"}},
        start="q0", accept={"q1"}, alphabet={"a", "b"},
    )
    dfa = nfa.to_dfa()
    for w in ["b", "ab", "aab", "abb", "", "a", "ba"]:
        assert nfa.accepts(w) == dfa.accepts(w)


def test_leet_idempotent():
    assert leet_normalize("4tt4ck") == "attack"
    assert leet_normalize("r0le") == "role"
    assert leet_normalize(leet_normalize("4tt4ck")) == leet_normalize("4tt4ck")


def test_fst_composition():
    swap = SequentialFST({("q", "a"): ("q", "b"), ("q", "b"): ("q", "a")}, "q", {"q"})
    t2 = SequentialFST({("q", "a"): ("q", "a"), ("q", "b"): ("q", "c")}, "q", {"q"})
    comp = compose(swap, t2)            # t2(swap(w))
    assert comp.transduce("ab") == "ca"


def test_miroir_twoway():
    assert reverse("kcatta") == "attack"


def test_delimiters_pda():
    assert well_parenthesized("[a(r)]") is True
    assert well_parenthesized("[a(r]") is False
    assert well_parenthesized("([)]") is False
    assert well_parenthesized("aor") is True
@@FILE@@ tests/test_cfg_nerode.py
from formlang.cfg import balanced_cfg
from formlang.myhill_nerode import nerode_classes, equivalent
from apps.shield.detector import contains_or


def test_cfg_engendre_des_mots_equilibres():
    G = balanced_cfg()
    mots = G.generate(max_len=4)
    assert "" in mots and "[]" in mots and "()" in mots
    assert "[a]" in mots and "[[]]" in mots
    assert "[" not in mots and "(]" not in mots


def test_nerode_trois_classes():
    words = ["", "a", "o", "ao", "or", "aor", "oo", "oa", "ror"]
    suffixes = ["", "r", "or", "a"]
    classes = nerode_classes(contains_or, words, suffixes)
    assert len(classes) == 3
    assert equivalent("o", "ao", contains_or, suffixes)
    assert not equivalent("o", "a", contains_or, suffixes)
@@FILE@@ tests/test_pipeline.py
from pipeline import analyze_word, analyze_morpho, demo_shield
from apps.morpho.corpora import corpus_A, corpus_B


def test_pipeline_word():
    r = analyze_word("4or")                 # -> 'aor' après normalisation
    assert r["normalisé(FST)"] == "aor"
    assert r["facteur_or(AFD)"] is True
    assert r["délimiteurs_ok(PDA)"] is True


def test_pipeline_morpho_suffixant():
    vocab = set(corpus_B())
    assert analyze_morpho("fafak", vocab)["classe(BUTA)"] == "BARE"
    assert analyze_morpho("fafaklar", vocab)["classe(BUTA)"] == "SUFFIXED"


def test_pipeline_morpho_prefixant():
    vocab = set(corpus_A())
    assert analyze_morpho("mufafak", vocab)["classe(BUTA)"] == "PREFIXED"


def test_demo_shield_verdicts():
    verdicts = dict(demo_shield())
    assert verdicts["sys(role)"] is True
    assert verdicts["role (isolé)"] is False
@@FILE@@ docs/PLACEHOLDER.md
# docs/

Les fiches pédagogiques (README racine, 00_overview, jour1..jour5,
RAPPORT_TEMPLATE) ont été fournies en Markdown dans le fil du projet.
Collez-les ici, ou demandez la variante « installateur docs » pour les écrire
automatiquement. Le LaTeX (énoncé + corrigé) sera généré après validation des
tests (pytest -q au vert).
'''


def parse_bundle(bundle: str) -> dict:
    files, path, buf = {}, None, []
    for line in bundle.splitlines(keepends=True):
        if line.startswith(MARK):
            if path is not None:
                files[path] = "".join(buf)
            path = line[len(MARK):].strip()
            buf = []
        elif path is not None:
            buf.append(line)
    if path is not None:
        files[path] = "".join(buf)
    return files


def main():
    ap = argparse.ArgumentParser(description="Installe le projet formlang.")
    ap.add_argument("--root", default=".", help="dossier cible (défaut: .)")
    ap.add_argument("--force", action="store_true", help="réécrit l'existant")
    args = ap.parse_args()

    files = parse_bundle(BUNDLE)
    written, skipped = 0, 0
    for rel, content in files.items():
        dst = os.path.join(args.root, rel)
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
        if os.path.exists(dst) and not args.force:
            print(f"  ~ existe, ignoré : {rel}")
            skipped += 1
            continue
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  + écrit : {rel}")
        written += 1

    print(f"\nTerminé : {written} écrit(s), {skipped} ignoré(s).")
    print("Étapes suivantes :")
    print("  pip install pytest")
    print("  pytest -q")
    print("  python pipeline.py        # démo Shield")
    print("  python pipeline.py --word 4or")
    print("  python pipeline.py --morpho mufafak")


if __name__ == "__main__":
    main()

