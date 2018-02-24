from client.client import run_client, mock_post_action_to_server, post_action_to_server
from nltk.corpus import wordnet as wn
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from functools import partial
import os


if __name__ == '__main__':
    # Preload the WordNet dictionary.
    print('Loading WordNet...')

    wn.ensure_loaded()

    # Train the ChatBot in case the transcript was not parsed as an action.
    print('Training Chat Bot...')

    chat_bot = ChatBot('James', read_only=True)
    chat_bot.set_trainer(ChatterBotCorpusTrainer)
    chat_bot.train("chatterbot.corpus.english")

    # Run the client in an infinite loop.
    print('Running Client...')
    cwd = os.getcwd()
    failure_responses_dir = os.path.join(cwd, 'client', 'failure_responses')

    #post = partial(post_action_to_server, 'http://192.168.0.30:8080/action')
    run_client(failure_responses_dir, chat_bot, mock_post_action_to_server)
