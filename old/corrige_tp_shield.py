"""
TP Théorie des langages — LLM-Secure Shield
SOLUTION DE RÉFÉRENCE (enseignant).

Alphabet abstrait Σ = {a, o, r, e, [, ], (, )} — aucun contenu sensible.
Lancer :   python3 corrige_tp_shield.py
"""

from typing import List, Union


# ===========================================================================
# PARTIE 1 — AFD pour L1 (facteur "or")
# ===========================================================================
def dfa_L1(w: str) -> bool:
    # AFD minimal à 3 états : A=init, B='o' vu, C=accepté (absorbant)
    delta = {
        ("A", "a"): "A", ("A", "o"): "B", ("A", "r"): "A",
        ("B", "a"): "A", ("B", "o"): "B", ("B", "r"): "C",
        ("C", "a"): "C", ("C", "o"): "C", ("C", "r"): "C",
    }
    state = "A"
    for c in w:
        state = delta[(state, c)]
    return state == "C"


# ===========================================================================
# PARTIE 2 — Transducteur leet
# ===========================================================================
LEET = {"4": "a", "3": "e", "0": "o", "1": "i", "5": "s"}


def leet_normalize(w: str) -> str:
    return "".join(LEET.get(c, c) for c in w)


# ===========================================================================
# PARTIE 3 — Automate à pile
# ===========================================================================
def well_parenthesized(w: str) -> bool:
    match = {"]": "[", ")": "("}
    stack: List[str] = []
    for c in w:
        if c in "[(":
            stack.append(c)
        elif c in match:
            if not stack or stack[-1] != match[c]:
                return False
            stack.pop()
        # a, o, r, e : pile inchangée
    return len(stack) == 0


# ===========================================================================
# PARTIE 4 — Automate d'arbres ascendant
# ===========================================================================
Term = Union[str, tuple]
SAFE, OVR, ROLE, DANGER = "q_safe", "q_ovr", "q_role", "q_danger"
SEVERITY = {SAFE: 0, OVR: 1, ROLE: 2}
_BY_SEVERITY = {0: SAFE, 1: OVR, 2: ROLE}


def tree_automaton(term: Term) -> str:
    # Feuilles (F1-F4)
    if isinstance(term, str):
        return {"txt": SAFE, "enc": SAFE, "ovr": OVR, "role": ROLE}[term]

    op = term[0]

    if op == "seq":
        left = tree_automaton(term[1])
        right = tree_automaton(term[2])
        # S1-S2 : le danger remonte
        if left == DANGER or right == DANGER:
            return DANGER
        # S3-S4 : annulation + rôle au même niveau
        if {left, right} == {OVR, ROLE}:
            return DANGER
        # S5 : fusion par sévérité
        return _BY_SEVERITY[max(SEVERITY[left], SEVERITY[right])]

    if op == "frame":
        child = tree_automaton(term[1])
        # C1-C4 : un ovr/role/danger dans une fiction => danger
        return SAFE if child == SAFE else DANGER

    if op == "sys":
        child = tree_automaton(term[1])
        # B1-B4 : un ovr/role/danger dans un faux bloc système => danger
        return SAFE if child == SAFE else DANGER

    raise ValueError(f"symbole inconnu : {op}")


def is_blocked(term: Term) -> bool:
    return tree_automaton(term) == DANGER


# ===========================================================================
# TESTS
# ===========================================================================
def _run_tests() -> None:
    # Partie 1
    assert dfa_L1("aor") is True
    assert dfa_L1("ora") is True
    assert dfa_L1("aoa") is False
    assert dfa_L1("") is False
    assert dfa_L1("oar") is False

    # Partie 2
    assert leet_normalize("4tt4ck") == "attack"
    assert leet_normalize("r0le") == "role"
    assert leet_normalize(leet_normalize("4tt4ck")) == leet_normalize("4tt4ck")

    # Partie 3
    assert well_parenthesized("[a(r)]") is True
    assert well_parenthesized("[a(r]") is False
    assert well_parenthesized("([)]") is False
    assert well_parenthesized("aor") is True

    # Partie 4
    assert is_blocked(("seq", "txt", "txt")) is False
    assert is_blocked("role") is False
    assert is_blocked(("sys", "role")) is True
    assert is_blocked(("seq", ("frame", "ovr"), "txt")) is True
    assert is_blocked(("sys", ("seq", "txt", ("frame", "role")))) is True

    # Cas supplémentaires (illustratifs)
    assert is_blocked(("seq", "ovr", "role")) is True   # S3
    assert is_blocked(("frame", "txt")) is False        # C3
    assert is_blocked(("sys", "txt")) is False          # B3

    print("✓ Tous les tests passent (solution de référence).")


if __name__ == "__main__":
    _run_tests()
