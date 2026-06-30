"""Transducteur fini séquentiel (one-way), lettre à lettre : une entrée -> une
sortie. Suffisant pour la normalisation (leet). Le MIROIR w -> w^R N'EST PAS
réalisable one-way (mémoire bornée) : il faudrait un transducteur bidirectionnel
-> voir reverse_twoway()."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SequentialFST:
    transitions: dict            # (state, in_sym) -> (next_state, out_sym)
    start: str
    finals: set
    identity_on_missing: bool = False   # émettre le symbole inchangé si absent

    def transduce(self, w: str) -> str:
        s, out = self.start, []
        for c in w:
            if (s, c) in self.transitions:
                s, o = self.transitions[(s, c)]
                out.append(o)
            elif self.identity_on_missing:
                out.append(c)                # boucle identité, état inchangé
            else:
                raise ValueError(f"transition manquante: ({s!r},{c!r})")
        return "".join(out)


def compose(t1: SequentialFST, t2: SequentialFST) -> SequentialFST:
    """t = t2 ∘ t1 : t(w) = t2(t1(w)). Tables EXPLICITES requises (pas
    d'identity_on_missing). États = paires (s1, s2)."""
    trans = {}
    for (s1, a), (s1n, b) in t1.transitions.items():
        for (s2, x), (s2n, c) in t2.transitions.items():
            if x == b:
                trans[((s1, s2), a)] = ((s1n, s2n), c)
    finals = {(f1, f2) for f1 in t1.finals for f2 in t2.finals}
    return SequentialFST(trans, (t1.start, t2.start), finals)


def leet_fst() -> SequentialFST:
    """4->a 3->e 0->o 1->i 5->s ; identité sinon. Un seul état q0 (final)."""
    leet = {"4": "a", "3": "e", "0": "o", "1": "i", "5": "s"}
    trans = {("q0", k): ("q0", v) for k, v in leet.items()}
    return SequentialFST(trans, "q0", {"q0"}, identity_on_missing=True)


def reverse_twoway(w: str) -> str:
    """Le renversement modélisé comme une transduction BIDIRECTIONNELLE
    (lecture jusqu'au bout puis émission de droite à gauche)."""
    return w[::-1]
