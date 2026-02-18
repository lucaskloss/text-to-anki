import PySide6.QtWidgets as QtWidgets

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

        # Input text area with file load button
        input_layout = QtWidgets.QHBoxLayout()
        self.input_text = QtWidgets.QTextEdit()
        self.input_text.setPlaceholderText("Enter or paste your text here...")
        input_layout.addWidget(self.input_text)
        self.load_file_button = QtWidgets.QPushButton("Load File...")
        input_layout.addWidget(self.load_file_button)
        layout.addLayout(input_layout)

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