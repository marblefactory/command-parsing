from client.speech_result import *
from chatterbot import ChatBot
from functools import partial
from speech.voice import say
import random
import requests


def post_action_to_server(server_address: str, action_json: str) -> Response:
    """
    :return: the response of sending the action json to the server.
    """
    return requests.post(server_address, action_json)


def mock_post_action_to_server(action_json: str) -> Response:
    """
    :return: a successful response.
    """
    r = Response()
    r.status_code = 200
    return r


def random_from_json(filename: str) -> str:
    """
    :return: opens the JSON file and chooses a random value from the array. Assumes there is an array at the top level.
    """
    with open(filename) as file:
        entries = json.load(file)
    return random.choice(entries)


def run_client(failure_responses_dir: str, chat_bot: ChatBot, post: Callable[[str], Response]):
    """
    :param failure_responses_dir: the path to the directory containing JSON files of failure responses.
    :param chat_bot: the chat bot used to generate responses for failure to parse actions.
    :return: infinitely loops recording audio, transcribing, parsing actions, and then sending the action to the server.
    """

    # TODO: Create path correctly (for Windows too)
    transcribe_fail_filename = failure_responses_dir + '/transcribe.json'
    server_fail_filename = failure_responses_dir + '/server.json'

    while True:
        input('Press Enter to record...')

        # Records audio and transcribes it.
        transcribed_result = record('output.wav') \
                            .then(transcribe) \
                            .then(partial(print_produce, 'transcribed:')) \
                            .map_failure(lambda _: random_from_json(transcribe_fail_filename))

        # Parses a transcript into an action.
        parsed_action = transcribed_result \
                       .then(parse_action) \
                       .then(partial(print_produce, 'action:')) \
                       .map_failure(lambda transcript: chat_bot.get_response(transcript))

        # Sends the action to the game server.
        server_response = parsed_action \
                         .then(partial(send_to_server, post)) \
                         .then(partial(print_produce, 'server response:')) \
                         .map_failure(lambda _: random_from_json(server_fail_filename))

        result = server_response.either(lambda value: value, lambda err: err)

        say(result)
