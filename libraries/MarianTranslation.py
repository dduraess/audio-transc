import re
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
            limits = (
                getattr(tokenizer, "model_max_length", None),
                getattr(model.config, "max_position_embeddings", None),
            )
            valid_limits = [
                limit
                for limit in limits
                if isinstance(limit, int) and 0 < limit < 1_000_000
            ]
            if not valid_limits:
                raise RuntimeError("Could not determine the Marian model input limit.")

            chunks = self._split_text(
                text.strip(), tokenizer, min(valid_limits)
            )
            translated_chunks = []
            for chunk in chunks:
                encoded = tokenizer([chunk], return_tensors="pt", padding=True)
                generated = model.generate(**encoded)
                translated_chunks.append(
                    tokenizer.batch_decode(
                        generated, skip_special_tokens=True
                    )[0].strip()
                )
            portuguese_text = " ".join(translated_chunks).strip()
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

    def translate_transcription_file_to_portuguese(
        self, transcription_path: str, source_language: str
    ) -> dict[str, str | bool]:
        """Translate a saved transcription and write only its text to saida-trad."""
        if not transcription_path:
            raise ValueError("Transcription file path was not provided.")

        source = Path(transcription_path).expanduser()
        if not source.is_file():
            raise FileNotFoundError(f"Transcription file does not exist: {source}")

        text = source.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"Transcription file is empty: {source}")

        destination = (
            Path(__file__).resolve().parents[1]
            / "saida-trad"
            / source.with_suffix(".pt.txt").name
        )
        return self.translate_text_to_portuguese(
            text, source_language, str(destination)
        )

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

    @staticmethod
    def _split_text(text: str, tokenizer: Any, max_input_tokens: int) -> list[str]:
        def token_count(value: str) -> int:
            return len(
                tokenizer(
                    value,
                    add_special_tokens=True,
                    verbose=False,
                )["input_ids"]
            )

        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: list[str] = []
        current = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if token_count(sentence) > max_input_tokens:
                if current:
                    chunks.append(current)
                    current = ""
                words = sentence.split()
                for word in words:
                    candidate = f"{current} {word}".strip()
                    if token_count(candidate) > max_input_tokens:
                        if not current:
                            raise ValueError(
                                "A single word exceeds the Marian model input limit."
                            )
                        chunks.append(current)
                        current = word
                    else:
                        current = candidate
                continue

            candidate = f"{current} {sentence}".strip()
            if current and token_count(candidate) > max_input_tokens:
                chunks.append(current)
                current = sentence
            else:
                current = candidate

        if current:
            chunks.append(current)
        return chunks
