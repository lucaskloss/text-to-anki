import spacy
from languages.base import LanguageProcessor

class GermanProcessor(LanguageProcessor):
    """
    Processes German text using spaCy for tokenization, lemmatization, and POS tagging.
    Can filter for content words and extract unique vocabulary.
    """
    
    # Fallback for common irregular verbs that spaCy may not lemmatize correctly
    VERB_FIXES = {
        'gegessen': 'essen',
        'gefressen': 'fressen',
        'gemessen': 'messen',
        'vergessen': 'vergessen',  # Already correct, but included for completeness
    }
    
    def __init__(self, nlp=None):
        """
        nlp: Optional, pass an existing spaCy model for efficiency.
        """
        if nlp is not None:
            self.nlp = nlp
        else:
            # Try to load the small model first (more widely compatible)
            try:
                self.nlp = spacy.load("de_core_news_sm")
            except OSError:
                # Fall back to large model if available
                try:
                    self.nlp = spacy.load("de_core_news_lg")
                except OSError:
                    raise OSError("No German spaCy model found. Please install one with: python -m spacy download de_core_news_sm")

    def process(self, text: str, content_words_only: bool = False):
        """
        Yields token information dicts for each token in the text.
        If content_words_only is True, yields only content words (NOUN, VERB, ADJ).
        """
        doc = self.nlp(text)
        for sent in doc.sents:
            for token in sent:
                # Apply lemma fixes for known irregular verbs
                lemma = token.lemma_.lower()
                if lemma in self.VERB_FIXES:
                    lemma = self.VERB_FIXES[lemma]
                
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

    def extract_unique_lemmas(self, text: str, content_words_only: bool = True):
        """
        Returns a set of unique lemmas from the text.
        If content_words_only is True, only content word lemmas are included.
        """
        return set(
            token["lemma"]
            for token in self.process(text, content_words_only=content_words_only)
        )