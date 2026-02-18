import spacy
from german_compound_splitter import comp_split
import io
from contextlib import redirect_stdout
from typing import Iterator

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

    def process(self, text: str) -> Iterator[dict]:
        """
        Yields token information dicts for each token in the text.
        """
        doc = self.nlp(text)
        for sent in doc.sents:
            for token in sent:
                # Apply lemma fixes for known irregular verbs
                lemma = token.lemma_.lower()
                
                token_info = {
                    "surface": token.text,
                    "lemma": lemma,
                    "pos": token.pos_,
                    "sentence": sent.text
                }
                if token_info["pos"] not in {"NOUN", "VERB", "ADJ"}:
                    continue
                yield token_info

    def extract_unique_lemmas(self, text) -> set:
        doc = self.nlp(text)
        lemmas = set()
        for token in doc:
            if (
            not token.is_alpha  # skip non-alphabetic tokens
            or token.is_stop    # skip stopwords
            or token.like_num   # skip numbers
            ):
                continue
            lemmas.add(token.lemma_.lower())
        return lemmas

    def build_compound_splitter(self, known_words):
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