import spacy

class SentenceSplitter:
	def __init__(self, language: str):
		if language == "de":
			self.nlp = spacy.load("de_core_news_lg")
		else:
			self.nlp = spacy.load("en_core_web_sm")

	def split(self, text: str) -> list[str]:
		"""
		Splits the input text into sentences.
		Returns a list of sentence strings.
		"""
		doc = self.nlp(text)
		return [sent.text.strip() for sent in doc.sents]
