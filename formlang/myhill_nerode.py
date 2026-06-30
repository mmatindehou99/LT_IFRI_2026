"""Congruence de Myhill-Nerode (sur les mots) : u ~ v ssi pour tout suffixe s,
(u s ∈ L) <=> (v s ∈ L). On l'approxime sur un ensemble FINI de suffixes témoins
pour relier le nombre de classes au nombre d'états de l'AFD minimal."""
from __future__ import annotations


def nerode_classes(accepts, words, suffixes):
    """Regroupe `words` par signature (acceptation de w+s pour s dans suffixes).
    Renvoie {signature: [mots...]}. Le nombre de classes minore le nombre d'états
    de l'AFD minimal (et l'égale si les suffixes sont distinguants)."""
    classes = {}
    for w in words:
        sig = tuple(accepts(w + s) for s in suffixes)
        classes.setdefault(sig, []).append(w)
    return classes


def equivalent(u, v, accepts, suffixes) -> bool:
    return all(accepts(u + s) == accepts(v + s) for s in suffixes)
