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
from actions.question import Question
from random import randrange
from interface.conversation_logging import log_conversation
from unittest.mock import Mock


app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, engineio_logger=True, async_mode='eventlet')

# If true, sends any parsed actions to the game, otherwise a successful response is generated without
# going to the game.
GAME_MODE = False

# The address of the game server. This will only be used if GAME_MODE is enabled.
GAME_SERVER = 'http://192.168.0.102:8080/'

# If True then the chatbot is trained fully. Otherwise the chatbot uses whatever it has been trained on.
TRAIN_CHATBOT = False

# If True, all tests are run before the server is started, thus filling the cache for the semantic similarity.
# This allows for responses to be generated more quickly.
FILL_CACHE = False

# Used to formulate a response if an action could not be parsed.
action_failed_chat_bot = ChatBot('Ethan')

def make_action_speech_response(game_response: GameResponse, action: Action) -> str:
    """
    :param game_response: the JSON response from the game.
    :param action: the action that was parsed.
    :return: the speech response to say to the user indicating whether or not the action was performed.
    """
    # Choose from negative or positive responses depending on whether the action could be performed.
    responses = action.positive_responses(game_response) if game_response['success'] else action.negative_responses()
    random_index = randrange(0, len(responses))
    speech_reply = responses[random_index]

    log_conversation('success reply', speech_reply)

    return speech_reply


def make_partial_speech_response(action_type) -> str:
    """
    :param action_type: the class of the action for which there was a partial parse.
    :return: a speech response indicating to give more information.
    """
    speech_reply = action_type.partial_response()
    log_conversation('partial reply', speech_reply)
    return speech_reply


def make_parse_failure_speech_response(transcript: str) -> str:
    """
    :param transcript: the transcript of what the user said.
    :return: the speech response to say to the user.
    """
    # 1 in 10 times use the chatbot to create a reply.
    if randrange(0, 9) == 0:
        r = action_failed_chat_bot.get_response(transcript)
    else:
        r = random_from_json('./failure_responses/action_parse.json')

    log_conversation('reply', r)
    return r


def make_speech_responder() -> SpeechResponder:
    """
    :return: a speech responder that parses actions and that responds to:
               - success with a random success speech from the action.
               - partial with speech determined by the type that failed to parse.
               - failure with speech from a chat bot,
    """
    return SpeechResponder(action(), make_action_speech_response, make_partial_speech_response, make_parse_failure_speech_response)


# Used to formulate responses to the user. This is initialised in main.
g_speech_responder: SpeechResponder = make_speech_responder()

def post_to_game(addr_postfix: str, action: Action) -> Response:
    """
    :return: the response of sending the action json to the server.
    """
    action_json = json.loads(json.dumps(action, cls=ActionEncoder))
    addr = GAME_SERVER + 'action'
    return requests.post(addr, json=action_json)


def mock_post_to_game(addr_postfix: str, action: Action) -> Mock:
    """
    :return: a successful response.
    """
    r = Mock(spec=Response)
    r.status_code = 200
    r.json.return_value = {
        'success': True,  # Indicates whether the action could be performed in the game.
        'inventory_item': 'rock',  # For if the user asks what the spy is carrying.
        'location': 'the computer lab',  # For if the user asks where the spy is.
        'num_guards': randrange(0, 10),  # For if the user asks about guards
        'surroundings': ['server', 'camera', 'camera'],  # For if the user asks about the spy's surroundings
        'mins_remaining': randrange(1, 5)
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
    log_conversation('transcript', transcript, print_nl_before=True)

    # The responder is used to keep track of state, such as whether the last transcript parsed to a partial.
    make_speech, action = g_speech_responder.parse(transcript)

    # If an action was parsed, send it to the server. The response is then dependent on whether the spy could
    # perform the action in the game, e.g. whether there was a rock to pick up.
    if action:
        log_conversation('action', action)

        # Where the action should be sent depends on whether it is a question or not.
        get_game_response = post_to_game if GAME_MODE else mock_post_to_game
        addr_postfix = 'questions' if isinstance(action, Question) else 'action'
        print('sending to:', addr_postfix)
        game_response = get_game_response(addr_postfix, action)

        log_conversation('server', game_response)

        try:
            game_json = game_response.json()
            log_conversation('server json', game_json)
        except:
            pass

        # We got a response from the server, however this does not mean the action was necessarily performed.
        # For example, if the spy was asked to pickup an object the action could fail if there are none of the
        # specified objects around.
        if game_response.status_code == 200:
            # TODO: Remove sample JSON
            sample_json = {
                'success': True,  # Indicates whether the action could be performed in the game.
                'inventory_item': 'rock',  # For if the user asks what the spy is carrying.
                'location': 'the computer lab',  # For if the user asks where the spy is.
                'num_guards': randrange(0, 10),  # For if the user asks about guards
                'surroundings': ['server', 'camera', 'camera'],  # For if the user asks about the spy's surroundings
                'mins_remaining': randrange(1, 5)
            }
            response = make_speech(sample_json)

            #response = make_speech(game_response.json())
        else:
            log_conversation('ERROR: Unsuccessful response from game', game_response)
            response = ''
    else:
        response = make_speech({})

    return response


def process_not_recognised_speech() -> str:
    """
    Speaks a response indicating that it the player was not understood.
    """
    return random_from_json('./failure_responses/transcription.json')


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

    trainer = ChatterBotCorpusTrainer if TRAIN_CHATBOT else ListTrainer
    action_failed_chat_bot.set_trainer(trainer)
    action_failed_chat_bot.train("chatterbot.corpus.english")

    if fill_cache:
        print('Filling Cache (Running Tests)...')
        loader = TestLoader()
        suite = loader.discover(start_dir='tests/parsing')
        TextTestRunner(verbosity=0).run(suite)


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
def handle_recognised_speech(transcript):
    # Create some response speech based on parsing and the response of the game server,
    # and give it to the client to speak.
    speech = process_transcript(transcript)
    emit('speech', str(speech))


@socketio.on('not_recognised')
def handle_not_recognised_speech(json):
    # Create some response speech and give it to the client to speak.
    speech = process_not_recognised_speech()
    emit('speech', speech)