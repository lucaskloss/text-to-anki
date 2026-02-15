from languages.german import GermanProcessor

def test_lemmatization():
    gp = GermanProcessor()
    tokens = list(gp.process("Ich ging nach Hause."))
    assert any(t["lemma"] == "gehen" for t in tokens)
