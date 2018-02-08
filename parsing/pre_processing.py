from typing import List


def pre_process(text: str) -> List[str]:
    """
    :return: takes the transcript of what the user said and turns it into a form that can be recognised by parsers.
    """
    return text.lower().split(' ')