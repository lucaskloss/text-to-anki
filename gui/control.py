import os

import PySide6.QtWidgets as QtWidgets

from export.csv_exporter import CSVExporter
from export.genanki_exporter import AnkiExporter
from gui.view import MainWindow
from languages.german import GermanProcessor
from languages.japanese import JapaneseProcessor
from load.audio_loader import transcribe_audio
from load.dictionary_loader import DictionaryLoader
from load.text_loader import TextLoader


AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac", ".webm", ".mp4"}
LANGUAGE_CODE_MAP = {
    "German": "de",
    "Japanese": "ja",
}

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
        self.view.load_audio_button.clicked.connect(self.load_audio_file)

    def _set_controls_enabled(self, enabled: bool):
        self.view.process_button.setEnabled(enabled)
        self.view.export_button.setEnabled(enabled)
        self.view.load_file_button.setEnabled(enabled)
        self.view.load_audio_button.setEnabled(enabled)
        self.view.browse_button.setEnabled(enabled)

    def _show_indeterminate_progress(self, status: str):
        self.view.status_label.setText(status)
        self.view.progress_bar.setVisible(True)
        self.view.progress_bar.setRange(0, 0)
        QtWidgets.QApplication.processEvents()

    def _show_progress(self, status: str, value: int, maximum: int):
        safe_maximum = max(1, maximum)
        bounded_value = max(0, min(value, safe_maximum))
        self.view.status_label.setText(status)
        self.view.progress_bar.setVisible(True)
        self.view.progress_bar.setRange(0, safe_maximum)
        self.view.progress_bar.setValue(bounded_value)
        QtWidgets.QApplication.processEvents()

    def _reset_progress(self, status: str = "Ready"):
        self.view.status_label.setText(status)
        self.view.progress_bar.setVisible(False)
        self.view.progress_bar.setRange(0, 100)
        self.view.progress_bar.setValue(0)
        QtWidgets.QApplication.processEvents()

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
                self._show_indeterminate_progress("Transcribing audio...")
                text, transcript_path = transcribe_audio(file_path, language=language_code)
                self.view.input_text.setPlainText(text)
                self.view.output_area.append(f"Loaded audio transcript: {transcript_path}")
            except Exception as error:
                self.view.output_area.append(f"\nFailed to transcribe audio: {error}")
            finally:
                self._reset_progress()
                self._set_controls_enabled(True)

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

        self._set_controls_enabled(False)
        try:
            self._show_progress("Analyzing text...", 0, 1)
            unique_lemmas = processor.extract_unique_lemmas(
                text,
                progress_callback=lambda current, total: self._show_progress(
                    f"Analyzing text... ({current}/{total} tokens)",
                    current,
                    total,
                ),
            )

            self._show_indeterminate_progress("Preparing dictionary lookup...")
            dictionary = DictionaryLoader(dict_dir)
            compound_splitter = None
            if language == "German":
                compound_splitter = processor.build_compound_splitter(dictionary.word_map.keys())

            sorted_lemmas = sorted(unique_lemmas)
            total_lemmas = len(sorted_lemmas)
            vocab_lines = []
            vocab_dict = {}
            translated_count = 0

            for index, lemma in enumerate(sorted_lemmas, start=1):
                self._show_progress(
                    f"Looking up dictionary... ({index}/{total_lemmas})",
                    index,
                    total_lemmas,
                )

                translations = dictionary.lookup(lemma)

                if not translations and language == "German":
                    normalized_lemma = processor.normalize_zu_infinitive(lemma)
                    if normalized_lemma and normalized_lemma != lemma:
                        translations = dictionary.lookup(normalized_lemma)

                if not translations and language == "German":
                    ge_candidates = processor.normalize_ge_participle_candidates(lemma)
                    for ge_candidate in ge_candidates:
                        if ge_candidate == lemma:
                            continue
                        translations = dictionary.lookup(ge_candidate)
                        if translations:
                            break

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
                    translated_count += 1
                    vocab_lines.append(f"{lemma}: {', '.join(translations[:3])}")
                else:
                    vocab_lines.append(f"{lemma}: [no translation found]")

            translation_rate = (translated_count / total_lemmas * 100) if total_lemmas else 0.0
            summary_line = (
                f"\n\nTranslated: {translated_count}/{total_lemmas} "
                f"({translation_rate:.1f}%)"
            )

            self.view.output_area.setPlainText("\n".join(vocab_lines) + summary_line)
            self.vocab_dict = vocab_dict
            self.last_text = text
            self._reset_progress(
                f"Done ({translated_count}/{total_lemmas} translated, {translation_rate:.1f}%)"
            )
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
