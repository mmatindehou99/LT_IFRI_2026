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
