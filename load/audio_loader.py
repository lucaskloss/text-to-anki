from pathlib import Path
import shutil

import whisper


_MODEL_CACHE = {}

_DEFAULT_MODEL_BY_LANGUAGE = {
    "ja": "small",
    "de": "base",
}


def _get_default_model(language: str | None) -> str:
    if not language:
        return "small"
    return _DEFAULT_MODEL_BY_LANGUAGE.get(language.lower(), "small")


def _load_model_cached(model_size: str):
    if model_size not in _MODEL_CACHE:
        _MODEL_CACHE[model_size] = whisper.load_model(model_size)
    return _MODEL_CACHE[model_size]


def _ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg is not installed or not in PATH. Install it with 'brew install ffmpeg' and restart the app."
        )


def transcribe_audio(audio_path, output_txt_path=None, model_size=None, language=None):
    """
    Transcribe an audio file with Whisper and optionally save it as a UTF-8 text file.

    Args:
        audio_path (str | Path): Path to the audio file.
        output_txt_path (str | Path | None): Output .txt path. If None, writes next to audio file.
        model_size (str | None): Whisper model ("tiny", "base", "small", "medium", "large").
            If None, a language-aware default is used.
        language (str | None): BCP-47/ISO language code (e.g. "ja", "de").
            Set this when known to improve speed and stability.

    Returns:
        tuple[str, Path]: (transcribed_text, output_file_path)
    """
    _ensure_ffmpeg_available()

    input_path = Path(audio_path)
    selected_model = model_size or _get_default_model(language)
    model = _load_model_cached(selected_model)

    transcribe_kwargs = {}
    if language:
        transcribe_kwargs["language"] = language.lower()

    try:
        result = model.transcribe(str(input_path), **transcribe_kwargs)
    except FileNotFoundError as error:
        if "ffmpeg" in str(error):
            raise RuntimeError(
                "ffmpeg is required for audio transcription. Install it with 'brew install ffmpeg' and restart the app."
            ) from error
        raise

    text = result["text"].strip()

    target_path = Path(output_txt_path) if output_txt_path else input_path.with_suffix(".txt")
    target_path.write_text(text, encoding="utf-8")

    return text, target_path