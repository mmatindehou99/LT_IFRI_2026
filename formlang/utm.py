"""Machine de Turing universelle.
U(<M> ## w) : on ENCODE M en une chaîne (donnée), puis U la DÉCODE et simule M
sur w. C'est tout le principe du programme enregistré / de l'interpréteur."""
from __future__ import annotations
import json
from .turing import TuringMachine, TMResult


def encode(machine: TuringMachine) -> str:
    """Linéarisation injective de M en JSON : <M>."""
    return json.dumps({
        "start": machine.start,
        "accept": sorted(machine.accept),
        "blank": machine.blank,
        "transitions": [[q, a, q2, b, d]
                        for (q, a), (q2, b, d) in machine.transitions.items()],
    }, sort_keys=True)


def decode(desc: str) -> TuringMachine:
    """Reconstruit M à partir de <M> (décodabilité)."""
    d = json.loads(desc)
    trans = {(q, a): (q2, b, dd) for q, a, q2, b, dd in d["transitions"]}
    return TuringMachine(trans, d["start"], set(d["accept"]), d.get("blank", "_"))


class UniversalTM:
    def run(self, encoded_machine: str, word: str, **kw) -> TMResult:
        """U lit la description encodée, la décode, puis simule sur w."""
        return decode(encoded_machine).run(word, **kw)
