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
        if nlp is not None:
            self.nlp = nlp
        else:
            # Try to load the small model first (more widely compatible)
            try:
                self.nlp = spacy.load("ja_core_news_md")
            except OSError:
                raise OSError("No Japanese spaCy model found. Please install one with: python -m spacy download ja_core_news_md")

    def process(self, text: str):
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

    def extract_unique_lemmas(self, text, progress_callback=None):
        doc = self.nlp(text)
        lemmas = set()
        total_tokens = len(doc)
        for index, token in enumerate(doc, start=1):
            if (
            not token.is_alpha  # skip non-alphabetic tokens
            or token.is_stop    # skip stopwords
            or token.like_num   # skip numbers
            ):
                if progress_callback and (index % 100 == 0 or index == total_tokens):
                    progress_callback(index, total_tokens)
                continue
            lemmas.add(token.lemma_.lower())

            if progress_callback and (index % 100 == 0 or index == total_tokens):
                progress_callback(index, total_tokens)

        return lemmas