"""Addition et soustraction unaires comme machines de Turing.
Tables tracées à la main (voir docs) ; à confirmer par tests/test_calc.py."""
from formlang.turing import TuringMachine

# ADD : 1^n + 1^m  ->  1^(n+m)
#   le '+' devient '1' (fusion des deux blocs), puis on efface UN '1' final.
ADD = TuringMachine(
    transitions={
        ("q0", "1"): ("q0", "1", "R"),
        ("q0", "+"): ("q1", "1", "R"),
        ("q1", "1"): ("q1", "1", "R"),
        ("q1", "_"): ("q2", "_", "L"),
        ("q2", "1"): ("qf", "_", "S"),
    },
    start="q0", accept={"qf"},
)

# SUB : 1^n - 1^m  ->  1^(n-m)  (tronquée, hypothèse n >= m)
#   on apparie un '1' de m (marqué X) avec un '1' de n (barré X, de droite à
#   gauche) ; quand m est épuisé, on nettoie X et '-', les '1' survivants de n
#   sont contigus à gauche -> sortie propre.
SUB = TuringMachine(
    transitions={
        ("q0", "1"): ("q0", "1", "R"), ("q0", "X"): ("q0", "X", "R"),
        ("q0", "-"): ("q1", "-", "R"),
        ("q1", "1"): ("q2", "X", "L"), ("q1", "X"): ("q1", "X", "R"),
        ("q1", "_"): ("q4", "_", "L"),
        ("q2", "X"): ("q2", "X", "L"), ("q2", "-"): ("q3", "-", "L"),
        ("q3", "1"): ("q0", "X", "R"), ("q3", "X"): ("q3", "X", "L"),
        ("q4", "X"): ("q4", "_", "L"), ("q4", "-"): ("q4", "_", "L"),
        ("q4", "1"): ("q4", "1", "L"), ("q4", "_"): ("qf", "_", "S"),
    },
    start="q0", accept={"qf"},
)
