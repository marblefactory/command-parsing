from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit
from client.speech_result import Success, print_produce, parse_action, send_to_server
from functools import partial
from requests import Response
from speech.voice import say
from nltk.corpus import wordnet as wn
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from threading import Thread
import requests
import json
import random

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Used to formulate a response if an action could not be parsed.
action_failed_chat_bot = ChatBot('James')


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


def process_transcript(transcript: str):
    """
    :return: parses the transcript into an action, then sends the action to the game server, then speaks a response.
    """
    print('transcript:', transcript)

    # Parse the transcript into an action.
    parsed_action = Success(transcript) \
        .then(partial(parse_action, lambda transcript: action_failed_chat_bot.get_response(transcript))) \
        .then(partial(print_produce, 'action:'))

    # Sends the action to the game server.
    server_response = parsed_action \
        .then(partial(send_to_server, lambda _: random_from_json('failure_responses/server.json'),
                      mock_post_action_to_game))

    speech_response = server_response.either(lambda value: value, lambda err: err)
    say(speech_response)


def process_not_recognised_speech():
    """
    Speaks a response indicating that it the player was not understood.
    """
    speech_response = random_from_json('failure_responses/transcribe.json')
    say(speech_response)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recognised', methods=['POST'])
def recognised_speech():
    """
    Called when the client recognised some speech.
    """
    transcript = request.get_json(silent=True)

    # Start a thread to parse the transcript and send it to the game since we don't know how long this will take.
    thread = Thread(target=process_transcript, args=[transcript])
    thread.start()

    return jsonify({})


@app.route('/not_recognised', methods=['POST'])
def not_recognised_speech():
    """
    Called when the user spoke, but we could not understand.
    """
    # Start a thread to parse the transcript and send it to the game since we don't know how long this will take.
    thread = Thread(target=process_not_recognised_speech)
    thread.start()

    return jsonify({})


def preload():
    # Preload the WordNet dictionary.
    print('Loading WordNet...')
    wn.ensure_loaded()

    # Train the ChatBot in case the transcript was not parsed as an action.
    print('Training Chat Bot...')
    #action_failed_chat_bot.set_trainer(ChatterBotCorpusTrainer)
    action_failed_chat_bot.set_trainer(ListTrainer)
    action_failed_chat_bot.train("chatterbot.corpus.english")


if __name__ == '__main__':
    preload()
    app.run()
