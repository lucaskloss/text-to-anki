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

    _SEPARABLE_PARTICLES = (
        "zusammen", "zurecht", "zurück", "entgegen", "empor", "entlang", "hinunter",
        "hinaus", "herein", "heraus", "herunter", "hinauf", "hinterher", "vorbei",
        "weiter", "wieder", "auseinander", "hinzu", "ab", "an", "auf", "aus", "bei",
        "ein", "fest", "fort", "her", "hin", "los", "mit", "nach", "nieder",
        "statt", "teil", "um", "unter", "vor", "weg", "zu"
    )

    _SENTENCE_END_PARTICLES = tuple(particle for particle in _SEPARABLE_PARTICLES if particle != "zu")

    def process(self, text: str) -> Iterator[dict]:
        """
        Yields token information dicts for each token in the text.
        """
        doc = self.nlp(text)
        for sent in doc.sents:
            for token in sent:
                token_info = {"surface": token.text, "lemma": token.lemma_.lower(),
                              "pos": token.pos_, "sentence": sent.text}
                if token_info["pos"] not in {"NOUN", "VERB", "ADJ"}:
                    continue
                yield token_info

    def extract_unique_lemmas(self, text, progress_callback=None) -> set:
        doc = self.nlp(text)
        lemmas = set()

        lemmas.update(self._extract_sentence_level_separable_verb_lemmas(doc))

        total_tokens = len(doc)
        for index, token in enumerate(doc, start=1):
            if token.dep_ == "svp":
                particle = token.lemma_.lower().strip()
                head = token.head
                if particle.isalpha() and head is not None and head.pos_ == "VERB":
                    verb_lemma = head.lemma_.lower().strip()
                    if verb_lemma.isalpha():
                        lemmas.add(f"{particle}{verb_lemma}")

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

    def _extract_sentence_level_separable_verb_lemmas(self, doc) -> set[str]:
        reconstructed_lemmas = set()

        for sent in doc.sents:
            trailing_particle = self._get_trailing_particle(sent)
            if not trailing_particle:
                continue

            main_verb = self._get_main_sentence_verb(sent)
            if not main_verb:
                continue

            particle = trailing_particle.lemma_.lower().strip()
            verb_lemma = main_verb.lemma_.lower().strip()
            if not particle.isalpha() or not verb_lemma.isalpha():
                continue

            reconstructed_lemmas.add(f"{particle}{verb_lemma}")

        return reconstructed_lemmas

    def _get_trailing_particle(self, sent):
        sentence_tokens = [token for token in sent if not token.is_punct and token.is_alpha]
        if not sentence_tokens:
            return None

        candidate = sentence_tokens[-1]
        if candidate.lemma_.lower() not in self._SENTENCE_END_PARTICLES:
            return None

        if candidate.pos_ not in {"ADP", "ADV", "PART"}:
            return None

        return candidate

    def _get_main_sentence_verb(self, sent):
        sentence_verbs = [token for token in sent if token.pos_ == "VERB" and token.lemma_.isalpha()]
        if not sentence_verbs:
            return None

        root_verb = next((token for token in sentence_verbs if token.dep_ == "ROOT"), None)
        if root_verb:
            return root_verb

        return sentence_verbs[0]

    def normalize_zu_infinitive(self, lemma: str) -> str | None:
        if not lemma:
            return None

        normalized = lemma.lower().strip()
        if len(normalized) < 6 or "zu" not in normalized:
            return None

        for particle in sorted(self._SEPARABLE_PARTICLES, key=len, reverse=True):
            prefix = f"{particle}zu"
            if not normalized.startswith(prefix):
                continue

            stem = normalized[len(prefix):]
            if len(stem) < 3 or not stem.isalpha():
                continue

            return f"{particle}{stem}"

        return None

    def normalize_ge_participle_candidates(self, lemma: str) -> list[str]:
        if not lemma:
            return []

        normalized = lemma.lower().strip()
        if len(normalized) < 5 or "ge" not in normalized:
            return []

        candidates = []

        for particle in sorted(self._SEPARABLE_PARTICLES, key=len, reverse=True):
            prefix = f"{particle}ge"
            if not normalized.startswith(prefix):
                continue

            stem = normalized[len(prefix):]
            if len(stem) < 3 or not stem.isalpha():
                continue

            candidates.append(f"{particle}{stem}")
            if stem.endswith("t") and len(stem) >= 4:
                candidates.append(f"{particle}{stem[:-1]}en")

        if normalized.startswith("ge"):
            stem = normalized[2:]
            if len(stem) >= 3 and stem.isalpha():
                candidates.append(stem)
                if stem.endswith("t") and len(stem) >= 4:
                    candidates.append(f"{stem[:-1]}en")

        deduped_candidates = []
        for candidate in candidates:
            if candidate not in deduped_candidates:
                deduped_candidates.append(candidate)

        return deduped_candidates

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