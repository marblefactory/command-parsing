from flask import Flask, render_template, send_from_directory, jsonify, request
from client.speech_result import Success, print_produce, parse_action, send_to_server
from functools import partial
from requests import Response
from speech.voice import say
from nltk.corpus import wordnet as wn
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
import requests
import json
import random

app = Flask(__name__, static_url_path='')

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


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognised', methods=['POST'])
def recognised_speech():
    transcript = request.get_json(silent=True)

    # Parse the transcript into an action.
    parsed_action = Success(transcript) \
        .then(partial(parse_action, lambda transcript: action_failed_chat_bot.get_response(transcript))) \
        .then(partial(print_produce, 'action:'))

    # Sends the action to the game server.
    server_response = parsed_action \
        .then(partial(send_to_server, lambda _: random_from_json('failure_responses/server.json'), mock_post_action_to_game))

    speech_response = server_response.either(lambda value: value, lambda err: err)
    say(speech_response)

    return jsonify({})


def preload():
    # Preload the WordNet dictionary.
    print('Loading WordNet...')
    wn.ensure_loaded()

    # Train the ChatBot in case the transcript was not parsed as an action.
    print('Training Chat Bot...')
    action_failed_chat_bot.set_trainer(ChatterBotCorpusTrainer)
    #action_failed_chat_bot.set_trainer(ListTrainer)
    action_failed_chat_bot.train("chatterbot.corpus.english")


if __name__ == '__main__':
    preload()
    app.run()
