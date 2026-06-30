"""Automate morphologique : prefix* root suffix*  (réutilise formlang.tree).
Classes : BARE / PREFIXED / SUFFIXED / CIRCUMFIXED."""
from formlang.tree import Term, TreeAutomaton

# --- constructeurs lisibles -------------------------------------------------
def prefix(s): return Term("prefix", label=s)
def root(s):   return Term("root",   label=s)
def suffix(s): return Term("suffix", label=s)
def nil():     return Term("nil")
def prefixes(h, t): return Term("prefixes", (h, t))
def suffixes(h, t): return Term("suffixes", (h, t))
def rest(r, s):     return Term("rest", (r, s))
def word(p, r):     return Term("word", (p, r))

def build_word(pres, root_str, sufs) -> Term:
    pc = nil()
    for p in reversed(pres): pc = prefixes(prefix(p), pc)
    sc = nil()
    for s in reversed(sufs): sc = suffixes(suffix(s), sc)
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
    if p and s: return "CIRCUMFIXED"
    if s:       return "SUFFIXED"
    if p:       return "PREFIXED"
    return "BARE"
