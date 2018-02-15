from client.client import run_client
from nltk.corpus import wordnet as wn


if __name__ == '__main__':
    # Preload the WordNet dictionary.
    print('Loading WordNet...')
    wn.ensure_loaded()

    run_client("http://192.168.0.30:8080/action")
