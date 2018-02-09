import os


def say(text: str, speaker = 'tom', words_per_min = 218):
    """
    Speaks the supplied text.
    """
    command = 'say -v "{}" -r {} "{}"'.format(speaker, words_per_min, text)
    os.system(command)
