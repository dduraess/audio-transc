from pathlib import Path
from typing import Any

from langdetect import DetectorFactory, LangDetectException, detect

class AudioTranscription:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    DetectorFactory.seed = 0

    def __init__(self, model_name: str = "small") -> None:
        self.model_name = model_name
        self._model: Any = None

    def transcribe_audio(
        self, audio_path: str, output_path: str | None = None
    ) -> dict[str, str]:
        """Transcribe an audio file and save the recognized text as UTF-8."""
        if not audio_path:
            raise ValueError("Audio file path was not provided.")

        source_path = Path(audio_path).expanduser()
        if not source_path.is_file():
            raise FileNotFoundError(f"Audio file does not exist: {source_path}")
        if source_path.stat().st_size == 0:
            raise ValueError(f"Audio file is empty: {source_path}")

        result = self._get_model().transcribe(str(source_path), task="transcribe")
        source_text = result.get("text", "").strip()
        if not source_text:
            raise RuntimeError("Whisper did not detect any speech in the audio.")

        destination = Path(output_path).expanduser() if output_path else self.get_transcription_output_path(
            str(source_path)
        )
        self._write_text(destination, source_text)

        return {
            "text": source_text,
            "output_path": str(destination.resolve()),
        }

    @staticmethod
    def get_transcription_output_path(audio_path: str) -> Path:
        """Return the default transcript path for an audio file."""
        source_path = Path(audio_path).expanduser()
        return (
            Path(__file__).resolve().parents[1]
            / "saida-transcr"
            / source_path.with_suffix(".txt").name
        )

    @staticmethod
    def detect_transcription_language(text: str) -> str:
        """Detect the language code of a transcribed text."""
        if not text or not text.strip():
            raise ValueError("Text to detect language from cannot be empty.")
        try:
            return detect(text.strip())
        except LangDetectException as error:
            raise RuntimeError(
                "Could not detect the language of the transcription."
            ) from error

    @staticmethod
    def _write_text(destination: Path, text: str) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text.strip() + "\n", encoding="utf-8")

    def _get_model(self) -> Any:
        if self._model is None:
            import whisper

            self._model = whisper.load_model(self.model_name)
        return self._model
