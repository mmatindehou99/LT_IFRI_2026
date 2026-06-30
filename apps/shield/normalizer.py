"""EnhancedNormalizer : normalisation leet (lettre à lettre) + miroir (two-way)."""
from formlang.fst import leet_fst, reverse_twoway

_LEET = leet_fst()


def leet_normalize(w: str) -> str:
    return _LEET.transduce(w)


def reverse(w: str) -> str:
    return reverse_twoway(w)
