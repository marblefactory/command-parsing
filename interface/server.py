import json
import random
from unittest import TestLoader, TextTestRunner
import requests
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from nltk.corpus import wordnet as wn
from requests import Response
from interface.speech_responder import SpeechResponder
from actions.action import Action
from encoders.encode_action import ActionEncoder
from parsing.parse_action import action
from actions.action import GameResponse
from random import randrange
from unittest.mock import Mock


app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, engineio_logger=True, async_mode='eventlet')

# If False, pre-loads the semantic similarity cache and trains the chat bot more throughly.
DEBUG_MODE = True

# If true, sends any parsed actions to the game, otherwise a successful response is generated without
# going to the game.
GAME_MODE = False

# The address of the game server. This will only be used if GAME_MODE is enabled.
GAME_SERVER = 'http://192.168.1.144:8080/action'

# Used to formulate a response if an action could not be parsed.
action_failed_chat_bot = ChatBot('James')

# Used to formulate responses to the user. This is initialised in main.
speech_responder: SpeechResponder = None


def post_action_to_game(action: Action) -> Response:
    """
    :return: the response of sending the action json to the server.
    """
    action_json = json.loads(json.dumps(action, cls=ActionEncoder))
    return requests.post(GAME_SERVER, json=action_json)


def mock_post_action_to_game(action: Action) -> Mock:
    """
    :return: a successful response.
    """
    r = Mock(spec=Response)
    r.status_code = 200
    r.json.return_value = {
        'success': True # Indicates whether the action could be performed in the game.
    }
    return r


def random_from_json(filename: str) -> str:
    """
    :return: opens the JSON file and chooses a random value from the array. Assumes there is an array at the top level.
    """
    with open(filename) as file:
        entries = json.load(file)
    return random.choice(entries)


def process_transcript(transcript: str) -> str:
    """
    :return: parses the transcript into an action, then sends the action to the game server, then speaks a response.
    """
    print('transcript:', transcript)

    # The responder is used to keep track of state, such as whether the last transcript parsed to a partial.
    make_speech, action = speech_responder.parse(transcript)

    # If an action was parsed, send it to the server. The response is then dependent on whether the spy could
    # perform the action in the game, e.g. whether there was a rock to pick up.
    if action:
        print('action:', action)

        game_response = post_action_to_game(action) if GAME_MODE else mock_post_action_to_game(action)

        print('server:', game_response)

        # We got a response from the server, however this does not mean the action was necessarily performed.
        # For example, if the spy was asked to pickup an object the action could fail if there are none of the
        # specified objects around.
        if game_response.status_code == 200:
            response = make_speech(game_response.json())
        else:
            print('ERROR: Unsuccessful response from game', game_response)
            response = ''
    else:
        response = make_speech({})

    return response


def process_not_recognised_speech() -> str:
    """
    Speaks a response indicating that it the player was not understood.
    """
    return random_from_json('failure_responses/transcribe.json')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_client_connect_event():
    print('Client connected')


@socketio.on('disconnect')
def handle_client_disconnected_event():
    print('Client disconnected')


@socketio.on('recognised')
def handle_recognised_speech(json):
    # Create some response speech based on parsing and the response of the game server,
    # and give it to the client to speak.
    speech = process_transcript(json)
    emit('speech', str(speech))


@socketio.on('not_recognised')
def handle_not_recognised_speech(json):
    # Create some response speech and give it to the client to speak.
    speech = process_not_recognised_speech()
    emit('speech', speech)


def preload(fill_cache: bool):
    """
    Pre-loads any data so the user experience is better, i.e. there is less delay during.
    :param fill_cache: if true, will run all parsing tests to fill the cache for the semantic distance function.
    """

    # Preload the WordNet dictionary.
    print('Loading WordNet...')
    wn.ensure_loaded()

    # Train the ChatBot in case the transcript was not parsed as an action.
    print('Training Chat Bot...')

    trainer = ListTrainer if DEBUG_MODE else ChatterBotCorpusTrainer
    action_failed_chat_bot.set_trainer(trainer)
    action_failed_chat_bot.train("chatterbot.corpus.english")

    if fill_cache:
        print('Filling Cache (Running Tests)...')
        loader = TestLoader()
        suite = loader.discover(start_dir='../tests/parsing')
        TextTestRunner(verbosity=0).run(suite)


def make_action_speech_response(game_response: GameResponse, action: Action) -> str:
    """
    :param game_response: the JSON response from the game.
    :param action: the action that was parsed.
    :return: the speech response to say to the user indicating whether or not the action was performed.
    """
    # Choose from negative or positive responses depending on whether the action could be performed.
    responses = action.positive_responses(game_response) if game_response['success'] else action.negative_responses()
    random_index = randrange(0, len(responses))
    return responses[random_index]


def make_partial_speech_response(action_type) -> str:
    """
    :param action_type: the class of the action for which there was a partial parse.
    :return: a speech response indicating to give more information.
    """
    return action_type.partial_response()


def make_parse_failure_speech_response(transcript: str) -> str:
    """
    :param transcript: the transcript of what the user said.
    :return: the speech response to say to the user.
    """
    r = action_failed_chat_bot.get_response(transcript)
    print('chatbot:', r)
    return r


def make_speech_responder() -> SpeechResponder:
    """
    :return: a speech responder that parses actions and that responds to:
               - success with a random success speech from the action.
               - partial with speech determined by the type that failed to parse.
               - failure with speech from a chat bot,
    """
    return SpeechResponder(action(), make_action_speech_response, make_partial_speech_response, make_parse_failure_speech_response)


if __name__ == '__main__':
    if not GAME_MODE:
        print("WARNING: Not in Game Mode")

    speech_responder = make_speech_responder()

    # Filling the cache takes a long time as all the tests have to run.
    preload(fill_cache=False)

    print('Running Server')
    socketio.run(app)
    #socketio.run(app, host='0.0.0.0')
