from pathlib import Path
from typing import Any


class MarianTranslation:
    ROBOT_LIBRARY_SCOPE = "SUITE"
    DEFAULT_MODEL = "Helsinki-NLP/opus-mt-tc-big-en-pt"

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        self.model_name = model_name
        self._model: Any = None
        self._tokenizer: Any = None

    def translate_text_to_portuguese(
        self, text: str, source_language: str, output_path: str
    ) -> dict[str, str | bool]:
        """Translate English text locally to Portuguese and save it as UTF-8."""
        if not text or not text.strip():
            raise ValueError("Text to translate cannot be empty.")
        if not source_language:
            raise ValueError("Source language was not provided.")
        if not output_path:
            raise ValueError("Output file path was not provided.")

        language = source_language.lower().split("-")[0]
        if language == "pt":
            portuguese_text = text.strip()
            translated = False
        elif language == "en":
            tokenizer, model = self._get_model()
            encoded = tokenizer([text.strip()], return_tensors="pt", padding=True)
            generated = model.generate(**encoded)
            portuguese_text = tokenizer.batch_decode(
                generated, skip_special_tokens=True
            )[0].strip()
            translated = True
        else:
            raise ValueError(
                "Marian translation supports English-to-Portuguese only; "
                f"received source language '{source_language}'."
            )

        if not portuguese_text:
            raise RuntimeError("Marian translation returned empty Portuguese text.")

        destination = Path(output_path).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(portuguese_text + "\n", encoding="utf-8")
        return {
            "text": portuguese_text,
            "translated": translated,
            "output_path": str(destination.resolve()),
        }

    def _get_model(self) -> tuple[Any, Any]:
        if self._model is None or self._tokenizer is None:
            from transformers import MarianMTModel, MarianTokenizer

            self._tokenizer = MarianTokenizer.from_pretrained(
                self.model_name, local_files_only=True
            )
            self._model = MarianMTModel.from_pretrained(
                self.model_name, local_files_only=True
            )
            self._model.eval()
        return self._tokenizer, self._model
