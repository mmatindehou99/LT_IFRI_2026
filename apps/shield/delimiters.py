"""Détection des délimiteurs [] () bien imbriqués (automate à pile)."""
from formlang.pda import DelimiterPDA

_PDA = DelimiterPDA()


def well_parenthesized(w: str) -> bool:
    return _PDA.accepts(w)

