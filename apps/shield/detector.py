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
