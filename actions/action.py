from typing import List
from equatable import EquatableMixin
from random import randrange


class Action(EquatableMixin):
    """
    An action that the player can command the spy to make.
    """

    def responses(self) -> List[str]:
        """
        :return: default affirmative responses that apply to all actions, plus any responses specific to the action.
        """
        #return self.specific_responses() + ['OK', 'Affirmative', 'Roger', 'Copy']
        if self.specific_responses() == []:
            return ['ok', 'affirmative', 'roger', 'copy', 'good idea']

        return self.specific_responses()

    def specific_responses(self):
        """
        :return: responses specific to the action.
        """
        return []

    def random_response(self) -> str:
        """
        :return: a random response from all possible responses to the action.
        """
        responses = self.responses()
        random_index = randrange(0, len(responses))
        return responses[random_index]


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
