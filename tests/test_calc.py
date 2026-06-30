from apps.calc.calculator import Calculatrice
from apps.calc.machines import ADD, SUB


def test_add_sub_machines_directes():
    assert ADD.run("111+11").tape.count("1") == 5
    assert SUB.run("111-11").tape.count("1") == 1
    assert SUB.run("11-11").tape == ""          # 2-2 = 0


def test_calculatrice_exhaustif():
    c = Calculatrice()
    for n in range(7):
        for m in range(7):
            assert c.addition(n, m) == n + m
            assert c.soustraction(n, m) == max(0, n - m)
            assert c.multiplication(n, m) == n * m
            if m:
                assert c.division(n, m) == divmod(n, m)


def test_chainage():
    c = Calculatrice()
    # (((2+1)*2)-1)//2 = 2
    assert c.chainer(2, [("+", 1), ("*", 2), ("-", 1), ("/", 2)]) == 2


def test_division_par_zero():
    import pytest
    with pytest.raises(ZeroDivisionError):
        Calculatrice().division(3, 0)
