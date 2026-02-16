import gradio as gr
import os
from languages.german import GermanProcessor
from languages.japanese import JapaneseProcessor
from core.dictionary_loader import DictionaryLoader
from anki.csv_exporter import CSVExporter
from anki.genanki_exporter import AnkiExporter

# Set default dictionary directories (relative to this file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_DIRS = {
    "German": os.path.abspath(os.path.join(BASE_DIR, "data", "kty-de-en")),
    "Japanese": os.path.abspath(os.path.join(BASE_DIR, "data", "kty-ja-en")),
}

# Global state for vocab_dict and last_text (per session)
session_state = {}

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
    vocab_lines = []
    vocab_dict = {}
    for lemma in sorted(unique_lemmas):
        translations = dictionary.lookup(lemma)
        vocab_dict[lemma] = translations
        if translations:
            vocab_lines.append(f"{lemma}: {', '.join(translations[:3])}")
        else:
            vocab_lines.append(f"{lemma}: [no translation found]")
    # Store in session state
    session_state["vocab_dict"] = vocab_dict
    session_state["last_text"] = text
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

def gradio_process(text, language, export_format, export_filename):
    output, vocab_dict = process_text(text, language)
    session_state["vocab_dict"] = vocab_dict
    return output, ""

def gradio_export(export_format, export_filename):
    vocab_dict = session_state.get("vocab_dict")
    result = export_vocab(vocab_dict, export_format, export_filename)
    return result

def gradio_load_file(file):
    if file is None:
        return ""
    try:
        content = file.read().decode("utf-8")
        return content
    except Exception as e:
        return f"Failed to load file: {e}"

with gr.Blocks() as demo:
    gr.Markdown("# Text to Anki Vocabulary Extractor")
    with gr.Row():
        language = gr.Dropdown(["German", "Japanese"], value="German", label="Language")
        export_format = gr.Dropdown(["CSV", "Anki", "Both"], value="CSV", label="Export Format")
    with gr.Row():
        input_text = gr.Textbox(lines=10, label="Input Text", placeholder="Enter or paste your text here...")
        file_input = gr.File(label="Load File", file_types=[".txt", ".epub", ".md", ".rtf", ".pdf"])
    with gr.Row():
        export_filename = gr.Textbox(label="Export File Name (e.g. output.csv or output.apkg)")
    process_btn = gr.Button("Process Text")
    export_btn = gr.Button("Export")
    output_area = gr.Textbox(label="Output", lines=10, interactive=False)
    export_result = gr.Textbox(label="Export Result", lines=2, interactive=False)

    # File loader
    file_input.change(fn=gradio_load_file, inputs=file_input, outputs=input_text)
    # Process button
    process_btn.click(fn=gradio_process, inputs=[input_text, language, export_format, export_filename], outputs=[output_area, export_result])
    # Export button
    export_btn.click(fn=gradio_export, inputs=[export_format, export_filename], outputs=export_result)

demo.launch()
