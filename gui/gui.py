import PySide6.QtWidgets as QtWidgets

from languages.german import GermanProcessor
from languages.japanese import JapaneseProcessor
from core.dictionary_loader import DictionaryLoader
from anki.csv_exporter import CSVExporter
from anki.genanki_exporter import AnkiExporter
import os

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text to Anki Vocabulary Extractor")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Language selection
        self.language_selector = QtWidgets.QComboBox()
        self.language_selector.addItems(["German", "Japanese"])
        layout.addWidget(self.language_selector)

        # Input text area
        self.input_text = QtWidgets.QTextEdit()
        self.input_text.setPlaceholderText("Enter or paste your text here...")
        layout.addWidget(self.input_text)

        # Export file selection
        file_layout = QtWidgets.QHBoxLayout()
        self.export_path = QtWidgets.QLineEdit()
        self.export_path.setPlaceholderText("Export file (e.g. output.csv or output.apkg)")
        file_layout.addWidget(self.export_path)
        self.browse_button = QtWidgets.QPushButton("Browse...")
        file_layout.addWidget(self.browse_button)
        layout.addLayout(file_layout)

        # Export format selection
        self.format_selector = QtWidgets.QComboBox()
        self.format_selector.addItems(["CSV", "Anki", "Both"])
        layout.addWidget(self.format_selector)

        # Process button
        self.process_button = QtWidgets.QPushButton("Process Text")
        layout.addWidget(self.process_button)

        # Export button
        self.export_button = QtWidgets.QPushButton("Export")
        layout.addWidget(self.export_button)

        # Output area
        self.output_area = QtWidgets.QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        # Connect buttons
        self.process_button.clicked.connect(self.process_text)
        self.export_button.clicked.connect(self.export_vocab)
        self.browse_button.clicked.connect(self.select_export_file)

        # Set default dictionary directories
        self.dict_dirs = {
            "German": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "kty-de-en")),
            "Japanese": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "kty-ja-en")),
        }
        self.vocab_dict = None
        self.last_text = None

    def process_text(self):
        text = self.input_text.toPlainText()
        if not text.strip():
            self.output_area.setPlainText("Please enter some text.")
            return

        language = self.language_selector.currentText()
        if language == "German":
            processor = GermanProcessor()
            dict_dir = self.dict_dirs["German"]
        elif language == "Japanese":
            processor = JapaneseProcessor()
            dict_dir = self.dict_dirs["Japanese"]
        else:
            self.output_area.setPlainText("Unsupported language selected.")
            return

        unique_lemmas = processor.extract_unique_lemmas(text)
        dictionary = DictionaryLoader(dict_dir)

        vocab_lines = []
        vocab_dict = {}
        for lemma in sorted(unique_lemmas):
            translations = dictionary.lookup(lemma)
            vocab_dict[lemma] = translations
            if translations:
                vocab_lines.append(f"{lemma}: {', '.join(translations[:3])}")
            else:
                vocab_lines.append(f"{lemma}: [no translation found]")

        self.output_area.setPlainText("\n".join(vocab_lines))
        self.vocab_dict = vocab_dict
        self.last_text = text

    def select_export_file(self):
        # Open file dialog for export file
        format = self.format_selector.currentText().lower()
        if format == "csv":
            filter = "CSV Files (*.csv);;All Files (*)"
        elif format == "anki":
            filter = "Anki Deck (*.apkg);;All Files (*)"
        else:
            filter = "All Files (*)"
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Select Export File", "", filter)
        if file_path:
            self.export_path.setText(file_path)

    def export_vocab(self):
        if not self.vocab_dict:
            self.output_area.setPlainText("Please process text first.")
            return
        export_path = self.export_path.text().strip()
        if not export_path:
            self.output_area.setPlainText("Please select an export file.")
            return
        format = self.format_selector.currentText().lower()
        try:
            if format in ["csv", "both"]:
                csv_path = export_path if export_path.endswith(".csv") or format == "csv" else export_path + ".csv"
                exporter = CSVExporter(csv_path)
                exporter.export(self.vocab_dict)
            if format in ["anki", "both"]:
                anki_path = export_path if export_path.endswith(".apkg") or format == "anki" else export_path + ".apkg"
                exporter = AnkiExporter(anki_path, deck_name="Vocabulary Deck")
                exporter.export(self.vocab_dict)
            self.output_area.append("\n✓ Export successful!")
        except Exception as e:
            self.output_area.append(f"\nExport failed: {e}")