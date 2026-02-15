import json
import os

class DictionaryLoader:
	def __init__(self, directory):
		self.directory = directory
		self.word_map = {}
		self._load_dictionary()

	def _extract_glosses_from_structured_content(self, content):
		"""
		Extract English glosses/translations from Yomichan structured-content format.
		Returns a list of translation strings.
		"""
		glosses = []
		
		if not isinstance(content, list):
			return glosses
		
		for item in content:
			if not isinstance(item, dict):
				continue
			
			# Look for the 'ol' (ordered list) tag with glosses
			if item.get('tag') == 'ol' and item.get('data', {}).get('content') == 'glosses':
				gloss_items = item.get('content', [])
				for gloss_item in gloss_items:
					if isinstance(gloss_item, dict) and gloss_item.get('tag') == 'li':
						# Extract text from this gloss item
						gloss_text = self._extract_text_from_gloss(gloss_item)
						if gloss_text:
							glosses.append(gloss_text)
			
			# Recursively search in nested content
			if 'content' in item:
				nested_glosses = self._extract_glosses_from_structured_content(
					item['content'] if isinstance(item['content'], list) else [item['content']]
				)
				glosses.extend(nested_glosses)
		
		return glosses

	def _extract_text_from_gloss(self, gloss_item):
		"""
		Extract the main translation text from a gloss list item.
		Filters out metadata like tags, examples, etc.
		"""
		texts = []
		
		def extract_text(obj, in_gloss_div=False):
			if isinstance(obj, str):
				texts.append(obj)
			elif isinstance(obj, dict):
				tag = obj.get('tag', '')
				data_content = obj.get('data', {}).get('content', '')
				
				# Skip tags section, examples, and other metadata
				if data_content in ['tags', 'examples', 'example-sentence', 'backlink', 
				                   'extra-info', 'details-entry-examples', 'preamble',
				                   'summary-entry', 'details-entry-Etymology']:
					return
				
				# Skip details and summary tags completely
				if tag in ['details', 'summary']:
					return
				
				# Process content
				content = obj.get('content')
				if content:
					if isinstance(content, list):
						for item in content:
							extract_text(item, in_gloss_div or tag == 'div')
					else:
						extract_text(content, in_gloss_div or tag == 'div')
			elif isinstance(obj, list):
				for item in obj:
					extract_text(item, in_gloss_div)
		
		extract_text(gloss_item.get('content', []))
		
		# Join and clean up the text
		result = ' '.join(texts).strip()
		# Remove multiple spaces
		result = ' '.join(result.split())
		return result if result else None

	def _load_dictionary(self):
		# Find all term_bank_*.json files in the directory
		files = [f for f in os.listdir(self.directory) if f.startswith("term_bank_") and f.endswith(".json")]
		for fname in sorted(files):
			path = os.path.join(self.directory, fname)
			with open(path, encoding="utf-8") as f:
				entries = json.load(f)
				# Yomichan format: [word, reading, tags, rule, score, definitions, sequence, term_tags]
				for entry in entries:
					if len(entry) < 6:
						continue
					
					word = entry[0]  # German word
					definitions = entry[5]  # Definition content
					
					# Extract glosses from definitions
					glosses = []
					if isinstance(definitions, list):
						for def_item in definitions:
							if isinstance(def_item, dict) and def_item.get('type') == 'structured-content':
								content = def_item.get('content', [])
								extracted = self._extract_glosses_from_structured_content(content)
								glosses.extend(extracted)
					
					if word and glosses:
						# Store translations (create or append)
						if word.lower() not in self.word_map:
							self.word_map[word.lower()] = []
						self.word_map[word.lower()].extend(glosses)

	def lookup(self, lemma):
		"""
		Returns a list of English translations for the given German lemma.
		"""
		return self.word_map.get(lemma.lower(), [])
