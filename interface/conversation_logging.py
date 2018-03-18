from typing import Any


def log_conversation(event: str, status: Any, print_nl_before = False):
    """
    Appends the text to the conversation log in the format 'event: status'. Useful for recovering what was said to
    the game.
    """
    pre = '\n' if print_nl_before else ''
    text = '{}{}: {}'.format(pre, event, status)
    print(text)
    with open('conversation_log.txt', 'a') as log_file:
        log_file.write(text + '\n')
