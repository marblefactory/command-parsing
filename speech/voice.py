import os


def say(text: str):
    """
    Speaks the supplied text.
    """
    speaker = 'tom'
    word_per_min = 215

    command = "say -v '{}' -r {} '{}'".format(speaker, word_per_min, text)

    os.system(command)
