from pathlib import Path

from AudioTranscription import AudioTranscription
from MarianTranslation import MarianTranslation


class ReportAssertions:
    def assert_empty_transcription_is_rejected(self, text: str) -> str:
        try:
            AudioTranscription.detect_transcription_language(text)
        except ValueError as error:
            message = str(error)
            if "Text to detect language from cannot be empty" not in message:
                raise AssertionError(
                    f"Unexpected language detection error: {message}"
                ) from error
            return message
        raise AssertionError("Empty transcription was accepted for language detection.")

    def assert_missing_audio_is_rejected(self, audio_path: str) -> str:
        try:
            AudioTranscription().transcribe_audio(audio_path)
        except FileNotFoundError as error:
            message = str(error)
            if "Audio file does not exist" not in message:
                raise AssertionError(f"Unexpected audio error: {message}") from error
            return message
        raise AssertionError("Missing audio file was accepted.")

    def assert_unsupported_language_is_rejected(
        self, text: str, source_language: str, output_path: str
    ) -> str:
        try:
            MarianTranslation().translate_text_to_portuguese(
                text, source_language, output_path
            )
        except ValueError as error:
            message = str(error)
            if "supports English-to-Portuguese only" not in message:
                raise AssertionError(
                    f"Unexpected translation error: {message}"
                ) from error
            return message
        raise AssertionError("Unsupported source language was accepted.")

    def assert_output_file_contains_text(
        self, output_path: str, expected_text: str
    ) -> None:
        output_file = Path(output_path)
        if not output_file.is_file():
            raise AssertionError(f"Expected output file was not created: {output_path}")
        actual_text = output_file.read_text(encoding="utf-8").strip()
        if actual_text != expected_text:
            raise AssertionError(
                f"Output file content mismatch: expected {expected_text!r}, "
                f"got {actual_text!r}."
            )

    def assert_transcription_saved_in_project_output_directory(
        self, output_path: str
    ) -> None:
        output_file = Path(output_path).resolve()
        expected_directory = (
            Path(__file__).resolve().parents[1] / "saida-transcr"
        ).resolve()
        if expected_directory not in output_file.parents:
            raise AssertionError(
                f"Expected transcription in {expected_directory}, got {output_file}."
            )

    def assert_translation_saved_in_project_output_directory(
        self, output_path: str
    ) -> None:
        output_file = Path(output_path).resolve()
        expected_directory = (
            Path(__file__).resolve().parents[1] / "saida-trad"
        ).resolve()
        if expected_directory not in output_file.parents:
            raise AssertionError(
                f"Expected translation in {expected_directory}, got {output_file}."
            )
