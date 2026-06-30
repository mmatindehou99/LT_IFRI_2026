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
                    clos.add(t); stack.append(t)
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
                    name[nxt] = f"S{n}"; n += 1; todo.append(nxt)
                trans[(name[cur], a)] = name[nxt]
        accept = {name[st] for st in name if any(s in self.accept for s in st)}
        return DFA(trans, name[start], accept, set(self.alphabet))
