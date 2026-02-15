import csv
import os


class CSVExporter:
    """
    Exports vocabulary and translations to a CSV file suitable for Anki import.
    """
    
    def __init__(self, output_path):
        """
        Args:
            output_path: Path to the output CSV file
        """
        self.output_path = output_path
    
    def export(self, vocab_dict):
        """
        Export vocabulary to CSV file.
        
        Args:
            vocab_dict: Dictionary mapping lemmas to lists of translations
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_path) if os.path.dirname(self.output_path) else '.', exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            
            # Write header
            writer.writerow(['Word', 'Translation'])
            
            # Write vocabulary entries
            for lemma in sorted(vocab_dict.keys()):
                translations = vocab_dict[lemma]
                if translations:
                    # Join translations with line breaks for better readability
                    translation_text = '<br>'.join(translations[:5])  # Limit to first 5 translations
                    writer.writerow([lemma, translation_text])
                else:
                    writer.writerow([lemma, '[no translation found]'])
        
        return self.output_path
    
    def export_with_context(self, vocab_data):
        """
        Export vocabulary with example sentences to CSV.
        
        Args:
            vocab_data: List of dicts with 'lemma', 'translations', and 'sentences' keys
        """
        os.makedirs(os.path.dirname(self.output_path) if os.path.dirname(self.output_path) else '.', exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            
            # Write header
            writer.writerow(['Word', 'Translation', 'Example'])
            
            # Write vocabulary entries
            for entry in vocab_data:
                lemma = entry['lemma']
                translations = entry.get('translations', [])
                sentences = entry.get('sentences', [])
                
                translation_text = '<br>'.join(translations[:5]) if translations else '[no translation found]'
                example_text = '<br>'.join(sentences[:3]) if sentences else ''
                
                writer.writerow([lemma, translation_text, example_text])
        
        return self.output_path
