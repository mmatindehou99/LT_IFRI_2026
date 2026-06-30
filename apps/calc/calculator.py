"""Calculatrice unaire. + et - sont de VRAIES MT (machines.py).
* et / sont des MACRO-machines : enchaînement contrôlé de ADD/SUB (les MT se
composent — c'est ce que fait une MTU qui orchestre des sous-machines)."""
from .machines import ADD, SUB


def _ones(s: str) -> int:
    return s.count("1")


class Calculatrice:
    def addition(self, n: int, m: int) -> int:
        return _ones(ADD.run("1" * n + "+" + "1" * m).tape)

    def soustraction(self, n: int, m: int) -> int:      # tronquée à 0
        if m > n:
            return 0
        return _ones(SUB.run("1" * n + "-" + "1" * m).tape)

    def multiplication(self, n: int, m: int) -> int:    # addition répétée
        acc = 0
        for _ in range(m):
            acc = self.addition(acc, n)
        return acc

    def division(self, n: int, m: int) -> tuple[int, int]:   # (quotient, reste)
        if m == 0:
            raise ZeroDivisionError("division par zéro")
        q, r = 0, n
        while r >= m:
            r = self.soustraction(r, m)
            q += 1
        return q, r

    def chainer(self, v0: int, ops: list[tuple[str, int]]) -> int:
        v = v0
        for op, k in ops:
            if op == "+":
                v = self.addition(v, k)
            elif op == "-":
                v = self.soustraction(v, k)
            elif op == "*":
                v = self.multiplication(v, k)
            elif op == "/":
                v, _ = self.division(v, k)
            else:
                raise ValueError(f"opérateur inconnu : {op!r}")
        return v
