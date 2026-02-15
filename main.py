
# Launch GUI by default, fallback to CLI if arguments are provided
import sys
def main():
	import argparse
	parser = argparse.ArgumentParser(description='Extract vocabulary from text and export to Anki or CSV (CLI mode). If no arguments are given, launches the GUI.')
	parser.add_argument('file_path', nargs='?', help='Path to the text file')
	parser.add_argument('dictionary_directory', nargs='?', help='Path to the dictionary directory')
	parser.add_argument('-o', '--output', help='Output file path (default: output.csv or output.apkg)')
	parser.add_argument('-f', '--format', choices=['csv', 'anki', 'both'], default='csv', help='Export format (default: csv)')
	args = parser.parse_args()

	if not args.file_path or not args.dictionary_directory:
		# Launch GUI
		from gui.gui import MainWindow
		from PySide6.QtWidgets import QApplication
		app = QApplication(sys.argv)
		window = MainWindow()
		window.show()
		app.exec()
		return

	# CLI mode (original logic)
	from core.text_loader import TextLoader
	from languages.german import GermanProcessor
	from core.dictionary_loader import DictionaryLoader
	from anki.csv_exporter import CSVExporter
	from anki.genanki_exporter import AnkiExporter

	print(f"Loading text from {args.file_path}...")
	loader = TextLoader(args.file_path)
	text = loader.load_text()

	print("Processing German text...")
	processor = GermanProcessor()
	unique_lemmas = processor.extract_unique_lemmas(text)

	print(f"Loading dictionary from {args.dictionary_directory}...")
	dictionary = DictionaryLoader(args.dictionary_directory)

	vocab_dict = {}
	for lemma in unique_lemmas:
		translations = dictionary.lookup(lemma)
		vocab_dict[lemma] = translations

	print(f"\nUnique lemmas found: {len(unique_lemmas)}")

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
