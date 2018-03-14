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
GAME_SERVER = 'http://192.168.0.16:8080/action'

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


def mock_post_action_to_game(action: Action) -> Response:
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


def process_transcript(transcript: str) -> str:
    """
    :return: parses the transcript into an action, then sends the action to the game server, then speaks a response.
    """
    print('transcript:', transcript)

    # The responder is used to keep track of state, such as whether the last transcript parsed to a partial.
    response, action = speech_responder.parse(transcript)

    # If an action was parsed, send it to the server. The response is then dependent on whether the spy could
    # perform the action in the game, e.g. whether there was a rock to pick up.
    if action:
        print('action:', action)

        game_response = post_action_to_game(action) if GAME_MODE else mock_post_action_to_game(action)

        print('response:', game_response)

        # If the spy could not perform the action, the speech response is replaced with one indicating that.
        if game_response.status_code != 200:
            response = random_from_json('failure_responses/server.json')

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


def make_speech_responder() -> SpeechResponder:
    """
    :return: a speech responder that parses actions and that responds to:
               - success with a random success speech from the action.
               - partial with speech determined by the type that failed to parse.
               - failure with speech from a chat bot,
    """
    success = lambda action: action.random_response()
    partial = lambda action_type: action_type.partial_response()
    failure = lambda transcript: action_failed_chat_bot.get_response(transcript)

    return SpeechResponder(action(), success, partial, failure)


if __name__ == '__main__':
    if not GAME_MODE:
        print("WARNING: Not in Game Mode")

    speech_responder = make_speech_responder()

    # Filling the cache takes a long time as all the tests have to run.
    preload(fill_cache=False)

    print('Running Server')
    socketio.run(app)
