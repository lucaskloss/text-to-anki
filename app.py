import os
import streamlit as st

from languages.german import GermanProcessor
from languages.japanese import JapaneseProcessor
from load.dictionary_loader import DictionaryLoader
from export.csv_exporter import CSVExporter
from export.genanki_exporter import AnkiExporter

# Set default dictionary directories (relative to this file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_DIRS = {
    "German": os.path.abspath(os.path.join(BASE_DIR, "data", "kty-de-en")),
    "Japanese": os.path.abspath(os.path.join(BASE_DIR, "data", "kty-ja-en")),
}

if 'vocab_dict' not in st.session_state:
    st.session_state['vocab_dict'] = None
if 'last_text' not in st.session_state:
    st.session_state['last_text'] = ""
if 'output_area' not in st.session_state:
    st.session_state['output_area'] = ""
if 'export_result' not in st.session_state:
    st.session_state['export_result'] = ""

def process_text(text, language):
    if not text.strip():
        return "Please enter some text.", None
    if language == "German":
        processor = GermanProcessor()
        dict_dir = DICT_DIRS["German"]
    elif language == "Japanese":
        processor = JapaneseProcessor()
        dict_dir = DICT_DIRS["Japanese"]
    else:
        return "Unsupported language selected.", None
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
    st.session_state["vocab_dict"] = vocab_dict
    st.session_state["last_text"] = text
    return "\n".join(vocab_lines), vocab_dict

def export_vocab(vocab_dict, export_format, export_filename):
    if not vocab_dict:
        return "Please process text first."
    if not export_filename.strip():
        return "Please enter an export file name."
    try:
        messages = []
        if export_format in ["CSV", "Both"]:
            csv_path = export_filename if export_filename.endswith(".csv") or export_format == "CSV" else export_filename + ".csv"
            exporter = CSVExporter(csv_path)
            exporter.export(vocab_dict)
            messages.append(f"CSV exported to {csv_path}")
        if export_format in ["Anki", "Both"]:
            anki_path = export_filename if export_filename.endswith(".apkg") or export_format == "Anki" else export_filename + ".apkg"
            exporter = AnkiExporter(anki_path, deck_name="Vocabulary Deck")
            exporter.export(vocab_dict)
            messages.append(f"Anki deck exported to {anki_path}")
        return "\n".join(messages) + "\n✓ Export successful!"
    except Exception as e:
        return f"Export failed: {e}"

st.title("Text to Anki Vocabulary Extractor")

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("Language", ["German", "Japanese"], index=0)
with col2:
    export_format = st.selectbox("Export Format", ["CSV", "Anki", "Both"], index=0)

uploaded_file = st.file_uploader("Load File", type=["txt", "epub", "md", "rtf", "pdf"])
if uploaded_file is not None:
    try:
        content = uploaded_file.read().decode("utf-8")
        if content != st.session_state.get("last_text", ""):
            st.session_state["last_text"] = content
            st.rerun()
    except Exception as e:
        st.error(f"Failed to load file: {e}")

input_text = st.text_area("Input Text", value=st.session_state.get("last_text", ""), height=200, placeholder="Enter or paste your text here...")

export_filename = st.text_input("Export File Name (e.g. output.csv or output.apkg)")

if st.button("Process Text"):
    if input_text.strip():
        output, _ = process_text(input_text, language)
        st.session_state["output_area"] = output
    else:
        st.session_state["output_area"] = "Please enter some text."

if st.button("Export"):
    vocab_dict = st.session_state.get("vocab_dict")
    result = export_vocab(vocab_dict, export_format, export_filename)
    st.session_state["export_result"] = result

# Display output area
if st.session_state.get("output_area"):
    st.text_area("Output", value=st.session_state["output_area"], height=200, disabled=True, key="output_display")

# Display export result
if st.session_state.get("export_result"):
    st.text_area("Export Result", value=st.session_state["export_result"], height=50, disabled=True, key="export_display")
