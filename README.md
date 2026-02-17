# text-to-anki
A Python tool to convert text into Anki flashcards, supporting multiple languages and formats. It uses spaCy for natural language processing and genanki for creating Anki decks. The tool can extract vocabulary, example sentences, and definitions to create effective flashcards for language learning.

The project is structured as follows:
- `main.py`: The entry point of the application, which launches the GUI.
- `gui/`: Contains the graphical user interface components.
- `anki/`: Contains the logic for creating Anki decks and cards.
- `core/`: Contains the core logic for processing text and generating flashcards.
- `data/`: Contains the dictionaries for different languages.
## Installation
1. Clone the repository:
```bash
git clone https://github.com/lucaskloss/text-to-anki.git
cd text-to-anki
```
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
3. Download the necessary spaCy models:
```bash
python -m spacy download de_core_news_md
python -m spacy download ja_core_news_md
```
4. Run the application:
```bash
python main.py
```

Note: Tested with Python 3.13, might not work with Python 3.14 versions because of compatibility issues with Spacy. To install a specific version of Python, you can use a version manager like `pyenv`. Here’s how you can install Python 3.13 using `pyenv`:

1. Install `pyenv` if you haven't already. You can follow the instructions on the [pyenv GitHub page](https://github.com/pyenv/pyenv).
2. Install Python 3.13 using `pyenv`:
```bash
pyenv install 3.13
```
3. Set the local Python version for the project:
```bash
pyenv local 3.13.14
```
4. Now you can proceed with installing the dependencies and running the application as mentioned above.
## Usage
1. Launch the application by running `python main.py`.
2. Use the GUI to input your text and configure the settings for your Anki flashcards.
3. Click the "Generate" button to create your Anki deck.
4. The generated Anki deck will be saved in the specified location, and you can import it into Anki to start studying.

The models used for processing the text are available at [spacy.io](https://spacy.io/models) and can be downloaded using the command line interface of spaCy. The models chosen are written in the setup.sh file, but you can change them if you want to use a different model or a custom one. The models used for the moment are the medium-sized models for German and Japanese, which provide a good balance between accuracy and speed. However, you can experiment with different models to see which one works best for your specific use case.
```

The only supported languages for now are German and Japanese, but more languages will be added in the future. The tool can handle various text formats, such as .txt, .epub, .pdf. The models used for the moment are simple and there is a lot of room for improvement. More features will be added in the future, including support for more languages, more text formats such as subtitle files, and more customization options for the flashcards. The most importants ones being the ability to add the example sentences from which the vocabulary was extracted, and the ability to filter the vocabulary by frequency or level. For instance, you could choose to only add words to a deck that are aimed at B2 or C1 learners and avoid adding more common words that you already know and would waste time reviewing or removing from the deck.

The dictionaries are obtained from [yomitan](https://yomidevs.github.io/kaikki-to-yomitan/) which has a convenient website for downloading dictionaries where you can choose between 18 languages from which to translate and the language of translation. The dictionaries are in JSON format and contain the word, its reading, its definition, and example sentences. The tool uses these dictionaries to create flashcards with the word, its reading, its definition, and an example sentence. The definitions are taken from the wiktionary database.