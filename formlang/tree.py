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
