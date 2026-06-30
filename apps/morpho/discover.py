"""De la SURFACE à l'ARBRE : découverte d'affixes par alternance avec ∅ (idée
de Z. Harris, 1955), segmentation gloutonne, puis l'arbre est VALIDÉ et CLASSÉ
par l'automate morphologique (apps/morpho/automaton.py)."""
from __future__ import annotations
from apps.morpho.automaton import build_word


def discover(vocab: set, prefix_side: bool, K: int = 3, maxn: int = 3) -> set:
    """Un affixe est retenu s'il alterne avec ∅ sur >= K racines attestées."""
    alt: dict[str, set] = {}
    for w in vocab:
        for n in range(1, maxn + 1):
            if len(w) <= n + 1:
                continue
            affix = w[:n] if prefix_side else w[-n:]
            stem = w[n:] if prefix_side else w[:-n]
            if stem in vocab:
                alt.setdefault(affix, set()).add(stem)
    return {a for a, roots in alt.items() if len(roots) >= K}


def segment_to_tree(w: str, PRE: set, SUF: set, maxn: int = 3):
    pres = []
    changed = True
    while changed:
        changed = False
        for n in range(maxn, 0, -1):
            if len(w) > n + 1 and w[:n] in PRE:
                pres.append(w[:n])
                w = w[n:]
                changed = True
                break
    rev = []
    changed = True
    while changed:
        changed = False
        for n in range(maxn, 0, -1):
            if len(w) > n + 1 and w[-n:] in SUF:
                rev.append(w[-n:])
                w = w[:-n]
                changed = True
                break
    sufs = list(reversed(rev))
    return build_word(pres, w, sufs)
