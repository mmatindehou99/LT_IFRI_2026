"""AttackDecomposer : automate d'arbres défensif, 100% structurel.
Jetons abstraits : txt, enc, ovr, role ; nœuds seq(2), frame(1), sys(1).
États : safe < ovr < role < danger. Bloqué ssi la racine est 'danger'."""
from formlang.tree import Term, TreeAutomaton

SAFE, OVR, ROLE, DANGER = "safe", "ovr", "role", "danger"
_SEV = {SAFE: 0, OVR: 1, ROLE: 2}
_BY_SEV = {0: SAFE, 1: OVR, 2: ROLE}
_ALL = (SAFE, OVR, ROLE, DANGER)


def _seq(x, y):
    if x == DANGER or y == DANGER:      # S1-S2 : le danger remonte
        return DANGER
    if {x, y} == {OVR, ROLE}:           # S3-S4 : annulation + rôle
        return DANGER
    return _BY_SEV[max(_SEV[x], _SEV[y])]   # S5 : sévérité max


def shield_automaton() -> TreeAutomaton:
    A = TreeAutomaton(final_states={DANGER})
    # feuilles (F1-F4)
    A.add_rule("txt",  (), SAFE)
    A.add_rule("enc",  (), SAFE)
    A.add_rule("ovr",  (), OVR)
    A.add_rule("role", (), ROLE)
    # seq : table complète sur 4x4 états
    for x in _ALL:
        for y in _ALL:
            A.add_rule("seq", (x, y), _seq(x, y))
    # frame / sys : un contenu non-safe dans une fiction / un faux bloc -> danger
    for x in _ALL:
        A.add_rule("frame", (x,), SAFE if x == SAFE else DANGER)
        A.add_rule("sys",   (x,), SAFE if x == SAFE else DANGER)
    return A


def txt():
    return Term("txt")


def enc():
    return Term("enc")


def ovr():
    return Term("ovr")


def role():
    return Term("role")


def seq(a, b):
    return Term("seq", (a, b))


def frame(a):
    return Term("frame", (a,))


def sys(a):
    return Term("sys", (a,))


def is_blocked(A: TreeAutomaton, t: Term) -> bool:
    return A.accepts(t)
