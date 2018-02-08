from google.cloud import speech
from google.cloud.speech import types
import io
from typing import Optional


def transcribe_file(file_name: str) -> Optional[str]:
    """
    :return: the text transcribed from the specified audio file, or None if no speech could be recognised.
    """

    client = speech.SpeechClient()

    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(language_code='en-US')

    response = client.recognize(config, audio)

    if len(response.results) == 0:
        return None

    return response.results[0].alternatives[0].transcript