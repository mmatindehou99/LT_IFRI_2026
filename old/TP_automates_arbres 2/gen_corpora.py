#!/usr/bin/env python3
# gen_corpora.py — génère deux mini-corpus SYNTHÉTIQUES à vérité-terrain connue,
# pour l'Exercice 4 du TP (segmentation + reconnaissance par l'automate d'arbres).
#
#   • Langue A — affixes en TÊTE de racine (préfixes).
#   • Langue B — affixes en QUEUE de racine (suffixes).
#
# Chaque corpus contient la racine NUE + toutes ses formes affixées ⇒ chaque affixe
# « alterne avec ∅ » sur toutes les racines : il est PRODUCTIF par construction.
# Déterministe (aucun aléa) : même sortie à chaque exécution.

PREFIXES_A = ["mu", "ba", "ki", "vi", "li", "ma", "wa", "tu"]   # 8 (vérité-terrain A)
SUFFIXES_B = ["lar", "ler", "im", "in", "de", "den", "si", "ya"]  # 8 (vérité-terrain B)

# Racines DÉTERMINISTES, conçues pour NE PAS se confondre avec les affixes :
#   • initiale ∈ {f,g,h,j,z,c,d,n,r,s} — AUCUNE initiale de préfixe (m,b,k,v,l,w,t)
#     ⇒ aucun préfixe spurieux dans la langue suffixante B.
#   • finale fixe "k" — AUCUN suffixe ne s'y greffe par hasard
#     ⇒ aucun suffixe spurieux dans la langue préfixante A.
# Résultat : vérité-terrain NETTE (A → 8 préfixes / 0 suffixe ; B → 8 suffixes / 0 préfixe).
CONS_INIT = "fghjzcdnrs"   # disjoint des initiales de préfixe
CONS_MID  = "fghjzcdnrs"
VOW       = "aeiou"
def roots(n):
    out = []
    for c1 in CONS_INIT:
        for v1 in VOW:
            for c2 in CONS_MID:
                for v2 in VOW:
                    out.append(c1 + v1 + c2 + v2 + "k")   # ex. "fafak", "zidek"…
                    if len(out) >= n:
                        return out
    return out

ROOTS = roots(150)   # 150 racines

def write(path, words):
    with open(path, "w") as f:
        for w in words:
            f.write(w + "\n")
    print(f"  écrit {path} : {len(words)} formes")

# Langue A : racine nue + préfixe+racine
A = []
for r in ROOTS:
    A.append(r)
    for p in PREFIXES_A:
        A.append(p + r)

# Langue B : racine nue + racine+suffixe
B = []
for r in ROOTS:
    B.append(r)
    for s in SUFFIXES_B:
        B.append(r + s)

if __name__ == "__main__":
    print("Vérité-terrain :")
    print(f"  Langue A (préfixante) : {len(PREFIXES_A)} préfixes {PREFIXES_A}")
    print(f"  Langue B (suffixante) : {len(SUFFIXES_B)} suffixes {SUFFIXES_B}")
    write("corpus_A_prefixing.txt", A)
    write("corpus_B_suffixing.txt", B)
