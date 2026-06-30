from formlang.dfa import DFA
from formlang.nfa import NFA
from formlang.fst import SequentialFST, compose, leet_fst
from apps.shield.detector import contains_or, detector_dfa
from apps.shield.normalizer import leet_normalize, reverse
from apps.shield.delimiters import well_parenthesized


def test_detector_or():
    assert contains_or("aor") is True
    assert contains_or("ora") is True       # contient 'or'
    assert contains_or("aoa") is False
    assert contains_or("") is False
    assert contains_or("oar") is False      # 'o' puis 'a' puis 'r' : pas adjacent

def test_minimisation_3_etats():
    assert detector_dfa().minimize().num_states() == 3

def test_nfa_to_dfa_equivalence():
    # AFN avec ε : accepte les mots finissant par 'b'
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
    assert well_parenthesized("([)]") is False     # chevauchement
    assert well_parenthesized("aor") is True

