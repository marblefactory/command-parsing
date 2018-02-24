from client.client import Client
from nltk.corpus import wordnet as wn


if __name__ == '__main__':
    # Preload the WordNet dictionary.
    print('Loading WordNet...')
    wn.ensure_loaded()

    client = Client(server_addr='http://192.168.0.30:8080/action',
                    audio_filename='output.wav',
                    transcribe_fail_responses_filename='client/failure_responses/transcribe.json',
                    spy_name='James Bond',
                    server_fail_responses_filename='client/failure_responses/server.json')

    client.run_loop()
