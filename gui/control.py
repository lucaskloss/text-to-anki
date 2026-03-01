import os

import PySide6.QtWidgets as QtWidgets

from export.csv_exporter import CSVExporter
from export.genanki_exporter import AnkiExporter
from gui.view import MainWindow
from languages.german import GermanProcessor
from languages.japanese import JapaneseProcessor
from languages.italian import ItalianProcessor
from load.audio_loader import transcribe_audio
from load.dictionary_loader import DictionaryLoader
from load.text_loader import TextLoader


AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac", ".webm", ".mp4"}
LANGUAGE_CODE_MAP = {
    "German": "de",
    "Japanese": "ja",
    "Italian": "it",
}

PROCESSORS = {
    "German": GermanProcessor(),
    "Japanese": JapaneseProcessor(),
    "Italian": ItalianProcessor(),
}

class MainController:
    def __init__(self):
        self.view = MainWindow()

        self.dict_dirs = {
            "German": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dictionaries", "kty-de-en")),
            "Japanese": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dictionaries", "kty-ja-en")),
            "Italian": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dictionaries", "kty-it-en")),
        }
        self.vocab_dict = None
        self.last_text = None

        self.view.process_button.clicked.connect(self.process_text)
        self.view.export_button.clicked.connect(self.export_vocab)
        self.view.browse_button.clicked.connect(self.select_export_file)
        self.view.load_file_button.clicked.connect(self.load_text_file)
        self.view.load_audio_button.clicked.connect(self.load_audio_file)

    def _set_controls_enabled(self, enabled: bool):
        self.view.process_button.setEnabled(enabled)
        self.view.export_button.setEnabled(enabled)
        self.view.load_file_button.setEnabled(enabled)
        self.view.load_audio_button.setEnabled(enabled)
        self.view.browse_button.setEnabled(enabled)

    def load_text_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.view,
            "Open Input File",
            "",
            "Text Files (*.txt *.epub *.md *.rtf *.pdf);;All Files (*)",
        )
        if file_path:
            try:
                loader = TextLoader(file_path)
                text = loader.load_text()
                self.view.input_text.setPlainText(text)
            except Exception as error:
                self.view.output_area.append(f"\nFailed to load file: {error}")

    def load_audio_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.view,
            "Open Audio File",
            "",
            "Audio Files (*.mp3 *.m4a *.wav *.flac *.ogg *.aac *.webm *.mp4);;All Files (*)",
        )
        if file_path:
            try:
                ext = os.path.splitext(file_path)[1].lower()
                if ext not in AUDIO_EXTENSIONS:
                    self.view.output_area.append("\nSelected file is not a supported audio format.")
                    return

                selected_language = self.view.language_selector.currentText()
                language_code = LANGUAGE_CODE_MAP.get(selected_language)
                self._set_controls_enabled(False)
                text, transcript_path = transcribe_audio(file_path, language=language_code)
                self.view.input_text.setPlainText(text)
                self.view.output_area.append(f"Loaded audio transcript: {transcript_path}")
            except Exception as error:
                self.view.output_area.append(f"\nFailed to transcribe audio: {error}")
            finally:
                self._set_controls_enabled(True)

    def process_text(self):
        text = self.view.input_text.toPlainText()
        if not text.strip():
            self.view.output_area.setPlainText("Please enter some text.")
            return

        language = self.view.language_selector.currentText()
        processor = PROCESSORS.get(language)
        dict_dir = self.dict_dirs.get(language)
        self._set_controls_enabled(False)
        
        try:
            processor.process(text)
            dictionary = DictionaryLoader(dict_dir)
            translated_count = 0
            for lemma in processor.vocabulary.keys():
                translations = dictionary.lookup(lemma)
                processor.vocabulary[lemma]["translations"] = translations
                if translations:
                    translated_count += 1

            translation_rate = (translated_count / len(processor.vocabulary) * 100)
            self.vocab_dict = processor.vocabulary
            self.last_text = text
            self.view.output_area.setPlainText(f"Processed {len(processor.vocabulary)} unique lemmas. Found translations for {translated_count} ({translation_rate:.1f}%).")
        finally:
            self._set_controls_enabled(True)

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
