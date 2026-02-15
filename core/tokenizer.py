import spacy

class Tokenizer:
	def __init__(self, language: str):
		if language == "de":
			self.nlp = spacy.load("de_core_news_lg")
		else:
			self.nlp = spacy.load("en_core_web_sm")  # fallback

	def tokenize(self, sentence: str) -> list[str]:
		"""
		Tokenizes a sentence into tokens.
		Returns a list of token strings.
		"""
		doc = self.nlp(sentence)
		return [token.text for token in doc]
