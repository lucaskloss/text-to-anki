import spacy
from languages.base import LanguageProcessor

class JapaneseProcessor(LanguageProcessor):
    """
    Processes Japanese text using spaCy for tokenization, lemmatization, and POS tagging.
    Can filter for content words and extract unique vocabulary.
    """
    
    def __init__(self, nlp=None):
        """
        nlp: Optional, pass an existing spaCy model for efficiency.
        """
        if nlp is not None:
            self.nlp = nlp
        else:
            # Try to load the small model first (more widely compatible)
            try:
                self.nlp = spacy.load("ja_core_news_sm")
            except OSError:
                # Fall back to large model if available
                try:
                    self.nlp = spacy.load("ja_core_news_lg")
                except OSError:
                    raise OSError("No Japanese spaCy model found. Please install one with: python -m spacy download ja_core_news_sm")

    def process(self, text: str, content_words_only: bool = True):
        """
        Yields token information dicts for each token in the text.
        If content_words_only is True, yields only content words (NOUN, VERB, ADJ).
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
                if content_words_only and not self.is_content_word(token_info):
                    continue
                yield token_info

    def is_content_word(self, token):
        """
        Returns True if the token dict is a content word (NOUN, VERB, ADJ).
        """
        return token["pos"] in {"NOUN", "VERB", "ADJ"}

    def extract_unique_lemmas(self, text):
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