import spacy

class Lemmatizer:
	def __init__(self, language: str):
		if language == "de":
			self.nlp = spacy.load("de_core_news_lg")
		else:
			self.nlp = spacy.load("en_core_web_sm")  # fallback

	def lemmatize(self, token_or_sentence: str):
		"""
		Lemmatizes a token or a sentence.
		If input is a string (sentence), returns list of lemmas.
		If input is a token string, returns its lemma.
		"""
		doc = self.nlp(token_or_sentence)
		if len(doc) == 1:
			return doc[0].lemma_
		else:
			return [token.lemma_ for token in doc]
