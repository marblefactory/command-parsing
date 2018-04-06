from parsing.parser import *


def player_name() -> Parser:
    """
    :return: a parser which parses the string name of the player, e.g. 'Albie' from 'I am Albie'
    """
    marker_names = ['neill', 'aisling', 'conor', 'carl', 'ian', 'tilo', 'beth', 'richard']
    markers = strongest_word(marker_names, make_word_parsers=[word_spelling])
    general = ignore_words(['i', 'name']).ignore_then(word_tagged(['NN', 'NNP']))

    return strongest([markers, general])
