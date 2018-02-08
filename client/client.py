from speech.record import Recorder
from speech.transcribe import transcribe_file
from parsing.parse_action import action
from parsing.pre_processing import pre_process
from encoders.encode_action import ActionEncoder
from speech.voice import say
import requests
import json
import random
from typing import List


def text_to_speech_failure_responses() -> List[str]:
    """
    :return: responses that can be said if the audio file could not be parsed.
    """
    return [
        'repeat?',
        'can you repeat?',
        'what was that command?'
    ]


def action_parse_failure_responses(transcript: str) -> List[str]:
    """
    :return: responses that can be said if an action could not be parsed from the transcript.
    """
    return [
        "I don't know how to '{}'".format(transcript),
        "I'm not sure how to do that",
        "that's not part of my training",
        "that's coming in a future update"
    ]


def action_perform_failure_response() -> List[str]:
    """
    :return: responses that can be said if the action could not be performed, e.g. there isn't a computer in the
             vicinity to hack.
    """
    return ["I can't do that"]


def run_client(server: str):
    """
    Runs an infinite loop of recording, transcribing, parsing, and sending to the server.
    """

    # Preload the wordnet dictionary.
    print('Loading WordNet...')
    action().parse(['a'])

    recorder = Recorder(sample_rate=16000)
    output_file_name = 'output.wav'

    while True:
        input('Press Enter start')

        recorder.record()
        recorder.write(output_file_name)

        transcript = transcribe_file(output_file_name)

        # If speech to text was unsuccessful.
        if not transcript:
            speech = random.choice(text_to_speech_failure_responses())
            say(speech)
            print()
            continue

        print('Transcribed     :', transcript)

        tokens = pre_process(transcript)
        result = action().parse(tokens)

        # If the text could not be parsed to an action.
        if not result:
            speech = random.choice(action_parse_failure_responses(transcript))
            say(speech)
            print()
            continue

        print('Parsed          :', result.parsed)

        response = requests.post(server, json=json.loads(json.dumps(result.parsed, cls=ActionEncoder)))

        print('Server Response :', response)

        if response.status_code != 200:
            speech = random.choice(action_perform_failure_response())
            say(speech)
            print()
            continue

        say(result.parsed.random_response())

        print()


if __name__ == '__main__':
    run_client("http://192.168.0.30:8080/action")
