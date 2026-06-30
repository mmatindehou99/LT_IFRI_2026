from formlang.tree import Term, product
from apps.morpho.automaton import morpho_automaton, build_word, classify
from apps.shield.decomposer import (
    shield_automaton, is_blocked, txt, enc, ovr, role, seq, frame, sys,
)

# ---- morphologie -----------------------------------------------------------
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
    assert classify(A, bad) == "INVALID"        # un suffixe à la place de la racine

# ---- shield (réutilise le MÊME coeur tree) ---------------------------------
def test_shield_blocage():
    A = shield_automaton()
    assert is_blocked(A, seq(txt(), txt()))                       is False
    assert is_blocked(A, role())                                  is False  # rôle isolé OK
    assert is_blocked(A, sys(role()))                             is True
    assert is_blocked(A, seq(frame(ovr()), txt()))               is True
    assert is_blocked(A, sys(seq(txt(), frame(role()))))         is True
    assert is_blocked(A, seq(ovr(), role()))                     is True   # annulation + rôle

# ---- clôture par intersection (produit) ------------------------------------
def _parite():           # accepte les arbres à nombre PAIR de feuilles 'a'
    from formlang.tree import TreeAutomaton
    A = TreeAutomaton(final_states={0})
    A.add_rule("a", (), 1); A.add_rule("b", (), 0)
    for x in (0, 1):
        for y in (0, 1):
            A.add_rule("c", (x, y), (x + y) % 2)
    return A

def _aumoins_un_a():     # accepte les arbres avec AU MOINS un 'a'
    from formlang.tree import TreeAutomaton
    A = TreeAutomaton(final_states={"yes"})
    A.add_rule("a", (), "yes"); A.add_rule("b", (), "no")
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
