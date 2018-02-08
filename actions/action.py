from typing import List
from equatable import EquatableMixin
import random


class Action(EquatableMixin):
    """
    An action that the player can command the spy to make.
    """

    def responses(self) -> List[str]:
        """
        :return: default affirmative responses that apply to all actions, plus any responses specific to the action.
        """
        return ['ok', 'affirmative', 'roger', 'roger that', 'copy', 'copy that'] + self.specific_responses()

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
