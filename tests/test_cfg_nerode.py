from formlang.cfg import balanced_cfg
from formlang.myhill_nerode import nerode_classes, equivalent
from apps.shield.detector import contains_or


def test_cfg_engendre_des_mots_equilibres():
    G = balanced_cfg()
    mots = G.generate(max_len=4)
    assert "" in mots and "[]" in mots and "()" in mots
    assert "[a]" in mots and "[[]]" in mots
    assert "[" not in mots and "(]" not in mots     # déséquilibrés exclus

def test_nerode_trois_classes():
    # 3 classes pour L1 (facteur 'or') = 3 états de l'AFD minimal
    words = ["", "a", "o", "ao", "or", "aor", "oo", "oa", "ror"]
    suffixes = ["", "r", "or", "a"]
    classes = nerode_classes(contains_or, words, suffixes)
    assert len(classes) == 3
    assert equivalent("o", "ao", contains_or, suffixes)      # tous deux "armés"
    assert not equivalent("o", "a", contains_or, suffixes)

