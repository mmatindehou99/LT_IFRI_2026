"""Génère deux mini-corpus déterministes : langue A préfixante, langue B
suffixante. Chaque racine apparaît nue + sous toutes ses formes affixées."""
PREFIXES_A = ["mu", "ba", "ki", "vi", "li", "ma", "wa", "tu"]
SUFFIXES_B = ["lar", "ler", "im", "in", "de", "den", "si", "ya"]
CONS = "fghjzcdnrs"     # initiales disjointes des préfixes ; finale 'k' fixe
VOW = "aeiou"


def roots(n: int):
    out = []
    for c1 in CONS:
        for v1 in VOW:
            for c2 in CONS:
                for v2 in VOW:
                    out.append(c1 + v1 + c2 + v2 + "k")
                    if len(out) >= n:
                        return out
    return out


def corpus_A(n_roots: int = 150) -> list:
    A = []
    for r in roots(n_roots):
        A.append(r)
        A += [p + r for p in PREFIXES_A]
    return A


def corpus_B(n_roots: int = 150) -> list:
    B = []
    for r in roots(n_roots):
        B.append(r)
        B += [r + s for s in SUFFIXES_B]
    return B
