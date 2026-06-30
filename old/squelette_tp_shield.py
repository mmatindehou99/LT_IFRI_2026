"""
TP Théorie des langages — LLM-Secure Shield
SQUELETTE ÉTUDIANT — à compléter là où il y a `# TODO`.

Aucun contenu sensible : on travaille sur l'alphabet abstrait
    Σ = {a, o, r, e, [, ], (, )}
où a=TXT, o=OVR, r=ROLE, e=ENC, et [ ] ( ) sont des délimiteurs.

Lancer les tests :   python3 squelette_tp_shield.py
(Les tests échouent tant que les fonctions ne sont pas complétées.)
"""

from dataclasses import dataclass
from typing import List, Union


# ===========================================================================
# PARTIE 1 — AFD reconnaissant L1 = { w sur {a,o,r} contenant le facteur "or" }
# ===========================================================================
def dfa_L1(w: str) -> bool:
    """
    Retourne True si le mot w contient le facteur 'or'.
    Implémenter SOUS FORME D'AUTOMATE (états A, B, C), pas avec 'in'.
    États : A=init, B='o' vu (armé), C=accepté (absorbant).
    """
    state = "A"
    for c in w:
        # TODO : écrire la table de transition de l'AFD minimal (Partie 1.3/1.4)
        raise NotImplementedError("dfa_L1 : à compléter")
    return state == "C"


# ===========================================================================
# PARTIE 2 — Transducteur fini : normalisation leetspeak
# ===========================================================================
LEET = {"4": "a", "3": "e", "0": "o", "1": "i", "5": "s"}


def leet_normalize(w: str) -> str:
    """
    Applique le transducteur leet lettre par lettre :
    4->a, 3->e, 0->o, 1->i, 5->s, et identité sinon.
    """
    # TODO : produire la sortie du transducteur (Partie 2.1)
    raise NotImplementedError("leet_normalize : à compléter")


# ===========================================================================
# PARTIE 3 — Automate à pile : prompt bien parenthésé sur [],()
# ===========================================================================
def well_parenthesized(w: str) -> bool:
    """
    True ssi les délimiteurs [ ] ( ) sont bien appariés et imbriqués.
    Les jetons a, o, r, e n'affectent pas la pile.
    Implémenter avec une PILE (automate à pile, Partie 3.4).
    """
    stack: List[str] = []
    for c in w:
        # TODO : gérer [ ] ( ) avec la pile ; ignorer a,o,r,e
        raise NotImplementedError("well_parenthesized : à compléter")
    return len(stack) == 0


# ===========================================================================
# PARTIE 4 — Automate d'arbres ascendant (AttackDecomposer)
# ===========================================================================
# Représentation d'un terme :
#   - feuille : une chaîne "txt" | "ovr" | "role" | "enc"
#   - noeud unaire  : ("sys", t) ou ("frame", t)
#   - noeud binaire : ("seq", t1, t2)
Term = Union[str, tuple]

# États de l'automate
SAFE, OVR, ROLE, DANGER = "q_safe", "q_ovr", "q_role", "q_danger"
SEVERITY = {SAFE: 0, OVR: 1, ROLE: 2}  # pour la règle de fusion S5


def tree_automaton(term: Term) -> str:
    """
    Évalue l'automate d'arbres ascendant et retourne l'état de la RACINE.
    Le prompt est BLOQUÉ ssi le résultat est DANGER.
    Règles : voir énoncé Partie 4.2 (F1-F4, S1-S5, C1-C4, B1-B4).
    """
    # Feuilles
    if isinstance(term, str):
        # TODO F1-F4 : txt/enc -> SAFE, ovr -> OVR, role -> ROLE
        raise NotImplementedError("tree_automaton (feuilles) : à compléter")

    op = term[0]

    if op == "seq":
        left = tree_automaton(term[1])
        right = tree_automaton(term[2])
        # TODO S1-S5 : propagation du danger / combinaison ovr+role / fusion
        raise NotImplementedError("tree_automaton (seq) : à compléter")

    if op == "frame":
        child = tree_automaton(term[1])
        # TODO C1-C4 : frame(ROLE)->DANGER, frame(OVR)->DANGER, ...
        raise NotImplementedError("tree_automaton (frame) : à compléter")

    if op == "sys":
        child = tree_automaton(term[1])
        # TODO B1-B4 : sys(ROLE)->DANGER, sys(OVR)->DANGER, ...
        raise NotImplementedError("tree_automaton (sys) : à compléter")

    raise ValueError(f"symbole inconnu : {op}")


def is_blocked(term: Term) -> bool:
    """Le Shield bloque-t-il ce prompt (arbre) ?"""
    return tree_automaton(term) == DANGER


# ===========================================================================
# TESTS (ne pas modifier)
# ===========================================================================
def _run_tests() -> None:
    # Partie 1
    assert dfa_L1("aor") is True
    assert dfa_L1("ora") is True
    assert dfa_L1("aoa") is False
    assert dfa_L1("") is False
    assert dfa_L1("oar") is False  # 'o' puis 'a' puis 'r' : pas de facteur "or"

    # Partie 2
    assert leet_normalize("4tt4ck") == "attack"
    assert leet_normalize("r0le") == "role"
    assert leet_normalize(leet_normalize("4tt4ck")) == leet_normalize("4tt4ck")

    # Partie 3
    assert well_parenthesized("[a(r)]") is True
    assert well_parenthesized("[a(r]") is False
    assert well_parenthesized("([)]") is False  # chevauchement
    assert well_parenthesized("aor") is True

    # Partie 4
    assert is_blocked(("seq", "txt", "txt")) is False          # (a)
    assert is_blocked("role") is False                          # (b) rôle isolé
    assert is_blocked(("sys", "role")) is True                  # (c)
    assert is_blocked(("seq", ("frame", "ovr"), "txt")) is True  # (d)
    assert is_blocked(("sys", ("seq", "txt", ("frame", "role")))) is True  # (e)

    print("✓ Tous les tests passent — bravo !")


if __name__ == "__main__":
    _run_tests()
