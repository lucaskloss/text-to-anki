import genanki
import random
import os
from export.note_model import create_note_model


class AnkiExporter:
    """
    Exports vocabulary to an Anki deck using genanki.
    """
    
    def __init__(self, output_path, deck_name="German Vocabulary"):
        """
        Args:
            output_path: Path to the output .apkg file
            deck_name: Name of the Anki deck
        """
        self.output_path = output_path
        self.deck_name = deck_name
        self.model = create_note_model()
        # Generate a random deck ID
        self.deck_id = random.randrange(1 << 30, 1 << 31)
    
    def export(self, vocab_dict):
        """
        Export vocabulary to Anki deck.
        
        Args:
            vocab_dict: Dictionary mapping lemmas to lists of translations
        """
        # Create deck
        deck = genanki.Deck(self.deck_id, self.deck_name)
        
        # Add notes to deck
        for lemma in sorted(vocab_dict.keys()):
            translations = vocab_dict[lemma]
            
            if translations:
                # Clean up translations - take first few and format them
                clean_translations = self._clean_translations(translations)
                translation_text = '<br>'.join(clean_translations)
            else:
                translation_text = '[no translation found]'
            
            # Create note
            note = genanki.Note(
                model=self.model,
                fields=[lemma, translation_text, '']
            )
            deck.add_note(note)
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(self.output_path) if os.path.dirname(self.output_path) else '.', exist_ok=True)
        
        # Generate package
        package = genanki.Package(deck)
        package.write_to_file(self.output_path)
        
        return self.output_path
    
    def export_with_context(self, vocab_data):
        """
        Export vocabulary with example sentences to Anki deck.
        
        Args:
            vocab_data: List of dicts with 'lemma', 'translations', and 'sentences' keys
        """
        # Create deck
        deck = genanki.Deck(self.deck_id, self.deck_name)
        
        # Add notes to deck
        for entry in vocab_data:
            lemma = entry['lemma']
            translations = entry.get('translations', [])
            sentences = entry.get('sentences', [])
            
            if translations:
                clean_translations = self._clean_translations(translations)
                translation_text = '<br>'.join(clean_translations)
            else:
                translation_text = '[no translation found]'
            
            # Format example sentences
            example_text = '<br><br>'.join(sentences[:3]) if sentences else ''
            
            # Create note
            note = genanki.Note(
                model=self.model,
                fields=[lemma, translation_text, example_text]
            )
            deck.add_note(note)
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(self.output_path) if os.path.dirname(self.output_path) else '.', exist_ok=True)
        
        # Generate package
        package = genanki.Package(deck)
        package.write_to_file(self.output_path)
        
        return self.output_path
    
    def _clean_translations(self, translations, max_count=5):
        """
        Clean and limit translations to make them more readable.
        
        Args:
            translations: List of translation strings
            max_count: Maximum number of translations to include
        
        Returns:
            List of cleaned translation strings
        """
        cleaned = []
        seen = set()
        
        for trans in translations[:max_count]:
            # Remove very long translations (likely full grammar explanations)
            if len(trans) > 200:
                continue
            
            # Remove duplicates
            trans_lower = trans.lower()
            if trans_lower in seen:
                continue
            
            seen.add(trans_lower)
            cleaned.append(trans)
        
        return cleaned
