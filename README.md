# Audio transcription tests

This Robot Framework suite separates audio transcription from text translation.
OpenAI Whisper transcribes the configured audio and saves the full recognized
text. A separate keyword detects the language from that text, and a local
MarianNMT model translates English transcriptions to Portuguese. Once the
Marian model is cached, translation runs without network access.

## Run

Install the dependencies in the active Python environment:

```sh
pip install -r requirements.txt
python -m scripts.download_translation_model
```

Set `AUDIO_FILE` to the audio file to transcribe and run the integration test:

```sh
AUDIO_FILE="/path/to/audio.mp3" robotcode robot tests/
```

The default Whisper model is `small`; pass
`--variable WHISPER_MODEL:base` (or another model name) to select a different
model. Whisper downloads the selected model on its first run. The MarianNMT
model is `Helsinki-NLP/opus-mt-tc-big-en-pt`; the setup command above downloads
it to the local Hugging Face cache. Translation accepts English (`en`) and
already-Portuguese (`pt`) text. Other source languages are rejected because
this model only translates English to Portuguese.

Language detection is a separate step from transcription and analyzes the
transcribed text locally. Very short or ambiguous text may not provide enough
information for reliable language detection.

The transcription is saved next to the audio file with a `.txt` suffix (for
example, `audio.mp3` produces `audio.txt`). The translation tests write their
Portuguese outputs in Robot Framework's output directory. `Transcribe And
Translate Audio Locally To Portuguese` tests the complete local flow when
`AUDIO_FILE` points to English or Portuguese speech. The suite also checks
unsupported languages and missing input files.
