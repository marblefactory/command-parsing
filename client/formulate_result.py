import json
import random
import requests
from chatterbot import ChatBot
from actions.action import Action
from client.speech_result import SpeechSuccess, SpeechFailure, SpeechResult
from encoders.encode_action import ActionEncoder
from parsing.parse_action import action
from parsing.pre_processing import pre_process
from speech.record import Recorder
from speech.transcribe import transcribe_file


def random_from_json(filename: str) -> str:
    """
    :return: opens the JSON file and chooses a random value from the array. Assumes there is an array at the top level.
    """
    with open(filename) as file:
        entries = json.load(file)
    return random.choice(entries)


def record(filename: str) -> SpeechResult:
    """
    :return: the a result containing the filename of where the recorded audio was written.
    """
    recorder = Recorder(sample_rate=41500)
    recorder.record()
    recorder.write(filename)

    return SpeechSuccess(filename)


def transcribe(fail_responses_filename: str, audio_filename: str) -> SpeechResult:
    """
    :param fail_responses_filename: the name of the JSON containing a list of failure responses.
    :return: result of transcribing the speech in the audio file with the given name. This fails if no speech could be
             recognised in the audio file.
    """
    transcript = transcribe_file(audio_filename)

    print('transcribed:', transcript)

    # If transcribing failed, open the JSON file containing failure responses and choose a random one.
    if not transcript:
        response = random_from_json(fail_responses_filename)
        return SpeechFailure(response)

    return SpeechSuccess(transcript)


def parse_action(fail_chatbot: ChatBot, transcript: str) -> SpeechResult:
    """
    :param fail_chatbot: the chatbot used to create responses if the speech was not recognised as an action.
    :return: result of parsing the speech transcript into actions. This fails if an action could not be parsed from the
             transcript.
    """
    words = pre_process(transcript)
    result = action().parse(words)

    print('parsed:', result)

    if not result:
        response = fail_chatbot.get_response(transcript)
        return SpeechFailure(response)

    return SpeechSuccess(result.parsed)


def send_to_server(fail_responses_filename: str, server_addr: str, parsed_action: Action) -> SpeechResult:
    """
    :param parsed_action: the action that was parsed from speech.
    :return: result of sending the action to the game to be performed. This fails if the game could not perform the
             action.
    """
    action_json = json.loads(json.dumps(parsed_action, cls=ActionEncoder))
    #response = requests.post(server_addr, json=action_json)
    response = 200

    print('server response:', response)

    #if response.status_code != 200:
    if response != 200:
        response = random_from_json(fail_responses_filename)
        return SpeechFailure(response)

    return SpeechSuccess(parsed_action.random_response())
