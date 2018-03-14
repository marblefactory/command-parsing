from parsing.parse_action import action
import time
import numpy as np
from typing import List
from nltk.corpus import wordnet as wn


action_transcripts = [
    'stop',
    'go through the door',
    'stand up',
    'turn around',
    'go to the second door on your left',
    'pick up the rock',
    'throw the rock',
    'hack the terminal behind you',
    'go forwards then go up the stairs',
    'hack the terminal then take the next left then go up stairs',
    'hack the camera and then go crouched to lab 300 and then run to the gun range'
    'stop then turn around then throw the rock',
    'hide behind the door',
    'go',
    'pickup'
]


def timed_parse(text: str) -> float:
    """
    :return: the time taken to parse the given text as an action.
    """
    start_time = time.time()

    result = action().parse(text.split())
    if not result:
        print('Failed to parse:', text)
        exit(0)

    end_time = time.time()

    return end_time - start_time


def timed_parse_avg(text: str) -> float:
    """
    :return: the average time from 20 parses to parse the given text.
    """
    num_iterations = 5
    times = [timed_parse(text) for _ in range(num_iterations)]
    return float(np.mean(times))


if __name__ == '__main__':
    # Preload WordNet so it doesn't affect the timing of the first parse.
    print('Loading WordNet...')
    wn.ensure_loaded()
    print('Starting Timing...\n')

    times: List[float] = []

    for text in action_transcripts:
        print("'{}'".format(text))

        t = timed_parse_avg(text)
        times.append(t)

        print('\ttook avg %.2fs\n' % t)

    print('Avg parse time: %.2fs' % np.mean(times))
