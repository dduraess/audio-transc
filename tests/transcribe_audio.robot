*** Settings ***
Documentation       Separate transcription and Portuguese translation tests.
Library             OperatingSystem
Library             ../libraries/AudioTranscription.py    model_name=${WHISPER_MODEL}
Library             ../libraries/MarianTranslation.py
Library             ../tests/ReportAssertions.py

*** Variables ***
${AUDIO_FILE}       ${EMPTY}
${TRANSCRIPTION_FILE}    ${EMPTY}
${WHISPER_MODEL}    base

*** Test Cases ***
Transcribe Audio And Save Full Transcript
    [Documentation]    Transcribes the configured audio and saves the complete recognized text.
    [Tags]    integration    transcription    whisper
    ${audio_file}=    Get Environment Variable    AUDIO_FILE    ${AUDIO_FILE}
    Should Not Be Empty    ${audio_file}    Set AUDIO_FILE to the path of an audio file.
    ${result}=    Transcribe Audio    ${audio_file}
    Should Not Be Empty    ${result}[text]
    Assert Transcription Saved In Project Output Directory    ${result}[output_path]
    File Should Exist    ${result}[output_path]
    Output File Should Contain Text    ${result}[output_path]    ${result}[text]

Detect Language From Transcription Text
    [Documentation]    Detects the language independently after transcription.
    [Tags]    unit    language-detection
    ${language}=    Detect Transcription Language
    ...    This is a complete English sentence used to verify language detection.
    Should Be Equal    ${language}    en

Translate English Text And Save Portuguese Output
    [Documentation]    Translates sample transcription text with the local Marian model.
    [Tags]    marian    translation
    ${output_path}=    Join Path    ${OUTPUT DIR}    translation.pt.txt
    ${result}=    Translate Text To Portuguese
    ...    Hello, how are you?
    ...    en
    ...    ${output_path}
    Should Be True    ${result}[translated]
    Should Be Equal    ${result}[text]    Olá, como estás?
    Output File Should Contain Text    ${result}[output_path]    ${result}[text]

Translate Saved Transcription File To Portuguese
    [Documentation]    Reads a saved transcript and writes only Portuguese text to saida-trad.
    [Tags]    integration    translation    marian
    ${transcription_file}=    Get Environment Variable    TRANSCRIPTION_FILE    ${TRANSCRIPTION_FILE}
    IF    not $transcription_file
        ${audio_file}=    Get Environment Variable    AUDIO_FILE    ${AUDIO_FILE}
        Should Not Be Empty    ${audio_file}    Set AUDIO_FILE or TRANSCRIPTION_FILE.
        ${transcription_file}=    Get Transcription Output Path    ${audio_file}
    END
    File Should Exist    ${transcription_file}
    ${source_text}=    Get File    ${transcription_file}    encoding=UTF-8
    ${source_language}=    Detect Transcription Language    ${source_text}
    ${result}=    Translate Transcription File To Portuguese
    ...    ${transcription_file}
    ...    ${source_language}
    Should Not Be Empty    ${result}[text]
    Assert Translation Saved In Project Output Directory    ${result}[output_path]
    Output File Should Contain Text    ${result}[output_path]    ${result}[text]
    IF    $source_language.lower().startswith("en")
        Should Be True    ${result}[translated]
    ELSE IF    $source_language.lower().startswith("pt")
        Should Be Equal    ${result}[translated]    ${False}
    END

Reject Empty Transcription For Language Detection
    [Documentation]    Rejects empty text when language detection is invoked separately.
    [Tags]    unit    validation    language-detection
    ${error}=    Assert Empty Transcription Is Rejected    ${EMPTY}
    Should Contain    ${error}    Text to detect language from cannot be empty

Preserve Portuguese Text Without Translation
    [Documentation]    Saves already-Portuguese text without loading Marian.
    [Tags]    unit    translation
    ${output_path}=    Join Path    ${OUTPUT DIR}    already-portuguese.pt.txt
    ${result}=    Translate Text To Portuguese
    ...    Bom dia.
    ...    pt-BR
    ...    ${output_path}
    Should Be Equal    ${result}[text]    Bom dia.
    Should Be Equal    ${result}[translated]    ${False}

Reject Unsupported Translation Language
    [Documentation]    Rejects unsupported languages rather than translating them incorrectly.
    [Tags]    unit    validation    translation
    ${output_path}=    Join Path    ${OUTPUT DIR}    unsupported-language.pt.txt
    ${error}=    Assert Unsupported Language Is Rejected    Hola.    es    ${output_path}
    Should Contain    ${error}    supports English-to-Portuguese only

Reject Missing Audio File
    [Documentation]    Fails clearly for a missing audio file without loading a Whisper model.
    [Tags]    unit    validation
    ${missing_audio}=    Join Path    ${OUTPUT DIR}    missing-audio-file.wav
    ${error}=    Assert Missing Audio Is Rejected    ${missing_audio}
    Should Contain    ${error}    Audio file does not exist

*** Keywords ***
Output File Should Contain Text
    [Arguments]    ${output_path}    ${expected_text}
    Assert Output File Contains Text    ${output_path}    ${expected_text}
