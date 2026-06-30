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
