from parsing.parser import SpeechParsable
from parsing.descriptor import Descriptor, WordMatch
from typing import List, Optional


class Action(SpeechParsable):
    """
    An action that the player can command the spy to make.
    """
    pass


class Stop(Action):
    """
    Tells the spy to stop whatever they're doing.
    """

    def __str__(self):
        return 'stop'

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        return WordMatch('stop')

    @classmethod
    def parse(cls, tokens: List[str]) -> Optional['Stop']:
        return Stop()
