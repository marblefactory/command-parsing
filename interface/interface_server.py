from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit
from client.speech_result import Success, print_produce, parse_action, send_to_server
from functools import partial
from requests import Response
from nltk.corpus import wordnet as wn
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
import requests
import json
import random
from unittest import TestLoader, TextTestRunner

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, engineio_logger=True, async_mode='eventlet')

# Used to formulate a response if an action could not be parsed.
action_failed_chat_bot = ChatBot('James')

# The address of the game server.
GAME_SERVER = '128.0.0.30:5000'


def post_action_to_game(server_address: str, action_json: str) -> Response:
    """
    :return: the response of sending the action json to the server.
    """
    return requests.post(server_address, action_json)


def mock_post_action_to_game(action_json: str) -> Response:
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

    # Parse the transcript into an action.
    parsed_action = Success(transcript) \
                   .then(partial(parse_action, lambda transcript: action_failed_chat_bot.get_response(transcript))) \
                   .then(partial(print_produce, 'action:'))

    # Sends the action to the game server.
    # post = partial(post_action_to_game, GAME_SERVER)
    # server_response = parsed_action \
    #                  .then(partial(send_to_server, lambda _: random_from_json('failure_responses/server.json'), post))

    server_response = parsed_action \
                     .then(partial(send_to_server, lambda _: random_from_json('failure_responses/server.json'), mock_post_action_to_game))

    return server_response.either(lambda value: value, lambda err: err)


def process_not_recognised_speech() -> str:
    """
    Speaks a response indicating that it the player was not understood.
    """
    return random_from_json('failure_responses/transcribe.json')


# @app.route('/js/<path:path>')
# def send_js(path):
#     return send_from_directory('js', path)


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
    #action_failed_chat_bot.set_trainer(ChatterBotCorpusTrainer)
    action_failed_chat_bot.set_trainer(ListTrainer)
    action_failed_chat_bot.train("chatterbot.corpus.english")

    if fill_cache:
        print('Filling Cache (Running Tests)...')
        loader = TestLoader()
        suite = loader.discover(start_dir='../tests/parsing')
        TextTestRunner(verbosity=0).run(suite)


if __name__ == '__main__':
    preload(fill_cache=True)

    print('Running Server')
    socketio.run(app)
