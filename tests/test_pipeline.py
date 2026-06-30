from pipeline import analyze_word, analyze_morpho, demo_shield
from apps.morpho.corpora import corpus_A, corpus_B


def test_pipeline_word():
    r = analyze_word("4or")                 # -> 'aor' après normalisation
    assert r["normalisé(FST)"] == "aor"
    assert r["facteur_or(AFD)"] is True
    assert r["délimiteurs_ok(PDA)"] is True

def test_pipeline_morpho_suffixant():
    vocab = set(corpus_B())
    # 'fafak' nu -> BARE ; 'fafaklar' -> SUFFIXED
    assert analyze_morpho("fafak", vocab)["classe(BUTA)"] == "BARE"
    assert analyze_morpho("fafaklar", vocab)["classe(BUTA)"] == "SUFFIXED"

def test_pipeline_morpho_prefixant():
    vocab = set(corpus_A())
    assert analyze_morpho("mufafak", vocab)["classe(BUTA)"] == "PREFIXED"

def test_demo_shield_verdicts():
    verdicts = dict(demo_shield())
    assert verdicts["sys(role)"] is True
    assert verdicts["role (isolé)"] is False

