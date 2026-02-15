# Pipeline: load text, process, extract vocabulary with translations, and export
import sys
import argparse
from core.text_loader import TextLoader
from languages.german import GermanProcessor
from core.dictionary_loader import DictionaryLoader
from anki.csv_exporter import CSVExporter
from anki.genanki_exporter import AnkiExporter


def main():
	parser = argparse.ArgumentParser(
		description='Extract vocabulary from text and export to Anki or CSV'
	)
	parser.add_argument('file_path', help='Path to the text file')
	parser.add_argument('dictionary_directory', help='Path to the dictionary directory')
	parser.add_argument('-o', '--output', help='Output file path (default: output.csv or output.apkg)')
	parser.add_argument('-f', '--format', choices=['csv', 'anki', 'both'], 
	                   default='csv', help='Export format (default: csv)')
	parser.add_argument('--no-print', action='store_true', 
	                   help='Do not print vocabulary to console')
	
	args = parser.parse_args()
	
	# Load and process text
	print(f"Loading text from {args.file_path}...")
	loader = TextLoader(args.file_path)
	text = loader.load_text()
	
	print("Processing German text...")
	processor = GermanProcessor()
	unique_lemmas = processor.extract_unique_lemmas(text)
	
	print(f"Loading dictionary from {args.dictionary_directory}...")
	dictionary = DictionaryLoader(args.dictionary_directory)
	
	# Build vocabulary dictionary
	vocab_dict = {}
	for lemma in unique_lemmas:
		translations = dictionary.lookup(lemma)
		vocab_dict[lemma] = translations
	
	print(f"\nUnique lemmas found: {len(unique_lemmas)}")
	
	# Print to console unless suppressed
	if not args.no_print:
		print("\nVocabulary:")
		print("-" * 80)
		for lemma in sorted(vocab_dict.keys()):
			translations = vocab_dict[lemma]
			if translations:
				# Show only first 3 translations for brevity
				preview = translations[:3]
				print(f"{lemma}: {', '.join(preview)}")
				if len(translations) > 3:
					print(f"  ... and {len(translations) - 3} more")
			else:
				print(f"{lemma}: [no translation found]")
		print("-" * 80)
	
	# Export
	export_format = args.format
	
	if export_format in ['csv', 'both']:
		if args.output and args.output.endswith('.csv'):
			csv_output = args.output
		elif args.output and export_format == 'csv':
			csv_output = args.output + '.csv'
		elif args.output:
			csv_output = args.output + '.csv'
		else:
			csv_output = 'output.csv'
		
		print(f"\nExporting to CSV: {csv_output}")
		exporter = CSVExporter(csv_output)
		exporter.export(vocab_dict)
		print(f"✓ CSV exported successfully to {csv_output}")
	
	if export_format in ['anki', 'both']:
		if args.output and args.output.endswith('.apkg'):
			anki_output = args.output
		elif args.output and export_format == 'anki':
			anki_output = args.output + '.apkg'
		elif args.output:
			anki_output = args.output + '.apkg'
		else:
			anki_output = 'output.apkg'
		
		print(f"\nExporting to Anki deck: {anki_output}")
		exporter = AnkiExporter(anki_output, deck_name="German Vocabulary")
		exporter.export(vocab_dict)
		print(f"✓ Anki deck exported successfully to {anki_output}")


if __name__ == "__main__":
	main()
