"""Grammaire hors-contexte minimale : génération bornée des mots dérivables
jusqu'à une longueur donnée (utile pour vérifier qu'une grammaire engendre bien
un langage). La reconnaissance générale (CYK) est laissée en extension."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CFG:
    rules: dict             # non-terminal -> liste de productions (tuples de symboles)
    start: str
    nonterminals: set

    def generate(self, max_len: int) -> set:
        """Mots terminaux dérivables, de longueur <= max_len (BFS sur les formes
        sententielles, élagué par la longueur des terminaux déjà produits)."""
        out, seen = set(), set()
        todo = [(self.start,)]
        while todo:
            form = todo.pop()
            if form in seen:
                continue
            seen.add(form)
            term_len = sum(1 for s in form if s not in self.nonterminals)
            if term_len > max_len:
                continue
            idx = next((i for i, s in enumerate(form) if s in self.nonterminals), None)
            if idx is None:
                out.add("".join(form))
                continue
            nt = form[idx]
            for prod in self.rules.get(nt, ()):
                new = form[:idx] + tuple(prod) + form[idx + 1:]
                if sum(1 for s in new if s not in self.nonterminals) <= max_len:
                    todo.append(new)
        return out


def balanced_cfg() -> CFG:
    """S -> S S | [ S ] | ( S ) | a | o | r | ε  (prompts bien parenthésés)."""
    return CFG(
        rules={"S": [("S", "S"), ("[", "S", "]"), ("(", "S", ")"),
                     ("a",), ("o",), ("r",), ()]},
        start="S", nonterminals={"S"},
    )
