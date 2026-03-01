import spacy
from german_compound_splitter import comp_split
import io
from contextlib import redirect_stdout

class GermanProcessor():
    """
    Processes German text using spaCy for tokenization, lemmatization, and POS tagging.
    Can filter for content words and extract unique vocabulary.
    """
    def __init__(self, nlp=None):
        """
        nlp: Optional, pass an existing spaCy model for efficiency.
        """
        self.nlp = nlp or spacy.load("de_core_news_md")
        self.vocabulary = {}

    def process(self, text: str):
        """
        Processes German text for vocabulary extraction.
        - Handles separable particle verbs by reconstructing their lemma.
        - Tracks first sentence, frequency, attached prepositions, attached particles.
        - Records grammatical case of verb arguments (subject, object, oblique).
        """
        doc = self.nlp(text)
        for sent in doc.sents:
            for token in sent:
                if token.pos_ not in {"NOUN", "VERB", "ADJ", "ADV"}:
                    continue
                lemma = token.lemma_.lower()
                cases = []
                prepositions = []
                if token.pos_ == "VERB":
                    for child in token.children:
                        if child.pos_ in {"NOUN", "PRON"} and child.morph.get("Case"):
                            cases.append(child.morph.get("Case")[0])
                        elif child.dep_ in {"ADP", "prep"}:
                            prepositions.append(child.text)
                        elif child.dep_ in {"prt", "svp"}:
                            lemma = f" {child.lemma_}" + lemma
                if lemma not in self.vocabulary:
                    self.vocabulary[lemma] = {"first sentence": sent.text, "frequency": 1,
                                              "cases": cases, "prepositions": prepositions}
                else:
                    self.vocabulary[lemma]["frequency"] += 1

    def build_compound_splitter(self, known_words):
        """Builds an Aho-Corasick automaton for efficient compound splitting based on known words."""
        automaton = comp_split.ahocorasick.Automaton()
        for word in known_words:
            if not word:
                continue
            normalized = word.lower().strip()
            if not normalized or len(normalized) < 3:
                continue
            automaton.add_word(normalized, (word[:1].isupper(), word))
        automaton.make_automaton()
        return automaton

    def split_compound(self, word, splitter):
        """Splits a compound word using the provided Aho-Corasick automaton splitter.
        """
        if not word or not splitter:
            return []

        with redirect_stdout(io.StringIO()):
            parts = comp_split.dissect(
                word,
                splitter,
                only_nouns=False,
                make_singular=False,
                mask_unknown=True,
            )

        if not parts or len(parts) < 2:
            return []

        normalized_parts = [part.lower() for part in parts if isinstance(part, str) and part.isalpha() and len(part) >= 3]
        if len(normalized_parts) < 2:
            return []

        return normalized_parts