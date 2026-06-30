"""Automate à pile déterministe pour délimiteurs imbriqués (langage de Dyck
multi-types + symboles ignorés). Acceptation par PILE VIDE."""
from __future__ import annotations


class DelimiterPDA:
    def __init__(self, pairs=(("[", "]"), ("(", ")")), ignore=("a", "o", "r", "e")):
        self.open = {o for o, _ in pairs}
        self.match = {c: o for o, c in pairs}     # fermant -> ouvrant attendu
        self.ignore = set(ignore)

    def accepts(self, w: str) -> bool:
        stack = []
        for c in w:
            if c in self.open:                    # empiler témoin
                stack.append(c)
            elif c in self.match:                 # dépiler si sommet correspond
                if not stack or stack[-1] != self.match[c]:
                    return False
                stack.pop()
            elif c in self.ignore:                # pile inchangée
                continue
            else:
                return False                      # symbole hors alphabet
        return len(stack) == 0                    # acceptation : pile vide
