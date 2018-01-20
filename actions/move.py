from actions.action import Action
from actions.locations import Location
from parsing.parser import SpeechParsable
from parsing.descriptor import *


class Speed(SpeechParsable):
    pass


class SlowSpeed(Speed):
    def __str__(self):
        return 'slow speed'

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        words = ['slow', 'slowly']
        return OneOf(WordMatch.list_from_words(words))

    @classmethod
    def parse(cls, tokens: List[str]) -> 'SlowSpeed':
        return cls()


class FastSpeed(Speed):
    def __str__(self):
        return 'fast speed'

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        words = ['fast', 'quickly', 'quick', 'run']
        return OneOf(WordMatch.list_from_words(words))

    @classmethod
    def parse(cls, tokens: List[str]) -> 'FastSpeed':
        return FastSpeed()

class NormalSpeed(Speed):
    def __str__(self):
        return 'normal speed'

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        return NoneOf([SlowSpeed.text_descriptor(), FastSpeed.text_descriptor()])

    @classmethod
    def parse(cls, tokens: List[str]) -> 'NormalSpeed':
        return NormalSpeed()


class Stance(SpeechParsable):
    pass


class Prone(Stance):
    def __str__(self):
        return 'prone'

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        return WordMatch('prone')

    @classmethod
    def parse(cls, tokens: List[str]) -> 'Prone':
        return Prone()


class Crouched(Stance):
    def __str__(self):
        return 'crouched'

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        words = ['crouch', 'crouched']
        return OneOf(WordMatch.list_from_words(words))

    @classmethod
    def parse(cls, tokens: List[str]) -> 'Crouched':
        return Crouched()

class Standing(Stance):
    def __str__(self):
        return 'standing'

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        return NoneOf([Prone.text_descriptor(), Crouched.text_descriptor()])

    @classmethod
    def parse(cls, tokens: List[str]) -> 'Standing':
        return Standing()


class Move(Action, SpeechParsable):
    """
    An action that tells the spy to move to a location.
    """

    def __init__(self, speed: Speed, stance: Stance, location: Location):
        self.speed = speed
        self.stance = stance
        self.location = location

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        words = ['go', 'move', 'step', 'head', 'proceed', 'follow', 'take', 'enter', 'exit']
