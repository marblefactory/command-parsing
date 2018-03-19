from typing import List
from equatable import EquatableMixin
from typing import Dict


# A JSON response from the game server to an action. This contains different information depending on the action.
# For example, for a question the response will contain the answer to the question.
GameResponse = Dict[str, str]


class ActionDefaultPositiveResponseMixin:
    """
    Mixin that provides some standard positive responses, e.g. 'OK, 'Affirmative', etc
    """

    def positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :return: default affirmative responses that apply to all actions, plus any responses specific to the action.
        """
        return self.specific_positive_responses(game_response) + ['OK', 'Affirmative', 'Roger', 'Copy']

    def specific_positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :return: responses specific to the action.
        """
        return []


class Action(EquatableMixin):
    """
    An action that the player can command the spy to make.
    """

    def positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :param game_response: the JSON object returned from the game server. The contents varies depending on the action sent.
        :return: a list of responses that can be used to speak to the player.
        """
        raise NotImplementedError

    def negative_responses(self) -> List[str]:
        """
        :return: a list of responses that can be spoken to the player to indicate that the spy cannot perform an action.
        """
        return ["I can't do that"]

    @classmethod
    def partial_response(cls) -> str:
        """
        :return: a question asking the player to give more information about this type they are trying to make.
        """
        raise NotImplementedError


class Stop(ActionDefaultPositiveResponseMixin, Action):
    """
    Tells the spy to stop whatever they're doing.
    """

    def __str__(self):
        return 'stop'

    def specific_positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :return: positive responses for the stop action. Does not expect anything to be given from the game.
        """
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
