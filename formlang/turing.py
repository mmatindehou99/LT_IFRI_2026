"""Machine de Turing déterministe, mono-ruban, ruban bi-infini (dict).
delta : (état, symbole) -> (état', symbole', direction ∈ {'L','R','S'})."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TMResult:
    accepted: bool
    tape: str            # ruban final, blancs de bord retirés
    steps: int
    trace: list = field(default_factory=list)


@dataclass
class TuringMachine:
    transitions: dict           # (q, a) -> (q', b, d)
    start: str
    accept: set
    blank: str = "_"
    reject: set = field(default_factory=set)

    def _read(self, tape: dict) -> str:
        if not tape:
            return ""
        lo, hi = min(tape), max(tape)
        s = "".join(tape.get(i, self.blank) for i in range(lo, hi + 1))
        return s.strip(self.blank)

    def _window(self, tape: dict) -> str:
        if not tape:
            return ""
        lo, hi = min(tape), max(tape)
        return "".join(tape.get(i, self.blank) for i in range(lo, hi + 1))

    def run(self, word: str, max_steps: int = 1_000_000, trace: bool = False) -> TMResult:
        tape = {i: c for i, c in enumerate(word)}
        pos, state, steps = 0, self.start, 0
        hist = []
        while steps < max_steps:
            sym = tape.get(pos, self.blank)
            if trace:
                hist.append((steps, state, pos, self._window(tape)))
            if state in self.accept:
                return TMResult(True, self._read(tape), steps, hist)
            if state in self.reject:
                return TMResult(False, self._read(tape), steps, hist)
            key = (state, sym)
            if key not in self.transitions:           # arrêt : aucune transition
                return TMResult(state in self.accept, self._read(tape), steps, hist)
            state, write, d = self.transitions[key]
            tape[pos] = write
            pos += 1 if d == "R" else -1 if d == "L" else 0
            steps += 1
        raise RuntimeError("max_steps dépassé — boucle infinie suspectée")
