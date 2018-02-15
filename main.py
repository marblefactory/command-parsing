from client.client import run_client
from parsing.parse_action import action


if __name__ == '__main__':
    # Preload the WordNet dictionary.
    print('Loading WordNet...')
    action().parse(['a'])

    run_client("http://192.168.0.30:8080/action")
