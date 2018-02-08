from typing import List
from equatable import EquatableMixin
from actions.respondable import Respondable
import random


class Action(EquatableMixin, Respondable):
    """
    An action that the player can command the spy to make.
    """

    def responses(self) -> List[str]:
        """
        :return: default responses that apply to all actions, plus any responses specific to the action.
        """
        return ['ok', 'affirmative', ''] + self.specific_responses()

    def specific_responses(self):
        """
        :return: responses specific to the action.
        """
        return []

    def random_response(self) -> str:
        """
        :return: a random response from all possible responses to the action.
        """
        return random.choice(self.responses())

    @staticmethod
    def negative_responses() -> List[str]:
        """
        :return: responses to indicate that the command was not understood.
        """
        return ['repeat?', 'can you repeat?', 'what was that command?']

    @staticmethod
    def random_negative_response() -> str:
        """
        :return: a random negative response from all available.
        """
        return random.choice(Action.negative_responses())


class Stop(Action):
    """
    Tells the spy to stop whatever they're doing.
    """

    def __str__(self):
        return 'stop'

    def specific_responses(self) -> List[str]:
        return ['stopping']


class Composite(Action):
    """
    An action made of multiple actions, e.g. go left then go right.
    """

    def __init__(self, actions: List[Action]):
        self.actions = actions

    def __str__(self):
        descriptions = [str(action) for action in self.actions]
        return ', then '.join(descriptions)
