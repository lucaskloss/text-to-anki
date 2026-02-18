import os

import PySide6.QtWidgets as QtWidgets

from export.csv_exporter import CSVExporter
from export.genanki_exporter import AnkiExporter
from gui.view import MainWindow
from languages.german import GermanProcessor
from languages.japanese import JapaneseProcessor
from load.dictionary_loader import DictionaryLoader


class MainController:
    def __init__(self):
        self.view = MainWindow()

        self.dict_dirs = {
            "German": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dictionaries", "kty-de-en")),
            "Japanese": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dictionaries", "kty-ja-en")),
        }
        self.vocab_dict = None
        self.last_text = None

        self.view.process_button.clicked.connect(self.process_text)
        self.view.export_button.clicked.connect(self.export_vocab)
        self.view.browse_button.clicked.connect(self.select_export_file)
        self.view.load_file_button.clicked.connect(self.load_text_file)

    def load_text_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.view,
            "Open Text File",
            "",
            "Text Files (*.txt *.epub *.md *.rtf *.pdf);;All Files (*)",
        )
        if file_path:
            try:
                from load.text_loader import TextLoader

                loader = TextLoader(file_path)
                text = loader.load_text()
                self.view.input_text.setPlainText(text)
            except Exception as error:
                self.view.output_area.append(f"\nFailed to load file: {error}")

    def process_text(self):
        text = self.view.input_text.toPlainText()
        if not text.strip():
            self.view.output_area.setPlainText("Please enter some text.")
            return

        language = self.view.language_selector.currentText()
        if language == "German":
            processor = GermanProcessor()
            dict_dir = self.dict_dirs["German"]
        elif language == "Japanese":
            processor = JapaneseProcessor()
            dict_dir = self.dict_dirs["Japanese"]
        else:
            self.view.output_area.setPlainText("Unsupported language selected.")
            return

        unique_lemmas = processor.extract_unique_lemmas(text)
        dictionary = DictionaryLoader(dict_dir)
        compound_splitter = None
        if language == "German":
            compound_splitter = processor.build_compound_splitter(dictionary.word_map.keys())

        vocab_lines = []
        vocab_dict = {}
        for lemma in sorted(unique_lemmas):
            translations = dictionary.lookup(lemma)

            if not translations and language == "German" and compound_splitter:
                split_parts = processor.split_compound(lemma, compound_splitter)
                if split_parts:
                    part_translation_lines = []
                    for part in split_parts:
                        part_translations = dictionary.lookup(part)
                        if not part_translations:
                            part_translation_lines = []
                            break
                        part_translation_lines.append(f"{part}: {', '.join(part_translations[:2])}")

                    if part_translation_lines:
                        translations = [f"[compound] {' + '.join(split_parts)}"] + part_translation_lines

            vocab_dict[lemma] = translations
            if translations:
                vocab_lines.append(f"{lemma}: {', '.join(translations[:3])}")
            else:
                vocab_lines.append(f"{lemma}: [no translation found]")

        self.view.output_area.setPlainText("\n".join(vocab_lines))
        self.vocab_dict = vocab_dict
        self.last_text = text

    def select_export_file(self):
        selected_format = self.view.format_selector.currentText().lower()
        if selected_format == "csv":
            dialog_filter = "CSV Files (*.csv);;All Files (*)"
        elif selected_format == "anki":
            dialog_filter = "Anki Deck (*.apkg);;All Files (*)"
        else:
            dialog_filter = "All Files (*)"

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.view,
            "Select Export File",
            "",
            dialog_filter,
        )
        if file_path:
            self.view.export_path.setText(file_path)

    def export_vocab(self):
        if not self.vocab_dict:
            self.view.output_area.setPlainText("Please process text first.")
            return

        export_path = self.view.export_path.text().strip()
        if not export_path:
            self.view.output_area.setPlainText("Please select an export file.")
            return

        selected_format = self.view.format_selector.currentText().lower()
        try:
            if selected_format in ["csv", "both"]:
                csv_path = export_path if export_path.endswith(".csv") or selected_format == "csv" else export_path + ".csv"
                exporter = CSVExporter(csv_path)
                exporter.export(self.vocab_dict)

            if selected_format in ["anki", "both"]:
                anki_path = export_path if export_path.endswith(".apkg") or selected_format == "anki" else export_path + ".apkg"
                exporter = AnkiExporter(anki_path, deck_name="Vocabulary Deck")
                exporter.export(self.vocab_dict)

            self.view.output_area.append("\n✓ Export successful!")
        except Exception as error:
            self.view.output_area.append(f"\nExport failed: {error}")
