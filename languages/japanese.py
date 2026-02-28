import spacy

class JapaneseProcessor():
    """
    Processes Japanese text using spaCy for tokenization, lemmatization, and POS tagging.
    Can filter for content words and extract unique vocabulary.
    """
    def __init__(self, nlp=None):
        """
        nlp: Optional, pass an existing spaCy model for efficiency.
        """
        self.nlp = nlp or spacy.load("ja_core_news_md")
        self.vocabulary = {}

    def process(self, text: str):
        """
        Processes Japanese text for vocabulary extraction.
        """
        doc = self.nlp(text)
        for sent in doc.sents:
            for token in sent:
                if token.pos_ not in {"NOUN", "VERB", "ADJ", "ADV"}:
                    continue
                lemma = token.lemma_.lower()
                if lemma not in self.vocabulary:
                    self.vocabulary[lemma] = {"first sentence": sent.text, "frequency": 1}
                else:
                    self.vocabulary[lemma]["frequency"] += 1