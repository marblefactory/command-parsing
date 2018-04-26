import inflect
from typing import List
from equatable import EquatableMixin
from typing import Dict, Any, Optional


# A JSON response from the game server to an action. This contains different information depending on the action.
# For example, for a question the response will contain the answer to the question.
GameResponse = Dict[str, Any]


class ActionErrorCode:
    GAME_ERROR = 0
    INVALID_LOCATION = 1
    COMPOSITE = 2
    INVALID_STAIRS = 3
    CANNOT_SEE = 4
    OUTSIDE_MAP = 5
    BLOCKED_MOVE = 6
    NOT_HOLDING = 7


class Action(EquatableMixin):
    """
    An action that the player can command the spy to make.
    """

    def positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :param game_response: the JSON object returned from the game server. The contents varies depending on the action sent.
        :return: a list of responses that can be used to speak to the player.
        """
        rs = self.specific_positive_responses(game_response)
        if rs == []:
            return ['OK', 'Affirmative', 'Roger', 'Copy']
        return rs

    def negative_responses(self, game_response: GameResponse) -> List[str]:
        """
        :return: a list of responses that can be spoken to the player to indicate that the spy cannot perform an action.
                 If the empty list is returned, the player will be asked to repeat the command.
        """
        error_code = game_response.get('error_code')
        subject = game_response.get('subject')

        if not error_code \
            or error_code == ActionErrorCode.GAME_ERROR \
            or error_code == ActionErrorCode.COMPOSITE:
            return []

        rs = self.specific_negative_responses(error_code, subject)
        if rs == []:
            return ["I can't do that"]
        return rs

    def specific_positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :return: responses specific to the action.
        """
        return []

    def specific_negative_responses(self, error_code: int, subject: Optional[str]) -> List[str]:
        """
        :return: responses specific to the action.
        """
        if error_code == ActionErrorCode.INVALID_LOCATION:
            return ["I can't go there"]

        elif error_code == ActionErrorCode.INVALID_STAIRS:
            return []

        elif error_code == ActionErrorCode.CANNOT_SEE:
            obj_name = inflect.engine().plural(text=subject) if subject else ''
            return ["I can't see any {}".format(obj_name)]

        elif error_code == ActionErrorCode.OUTSIDE_MAP:
            return ["I can't go there"]

        elif error_code == ActionErrorCode.BLOCKED_MOVE:
            obj_name = inflect.engine().a(text=subject) if subject else 'something'
            return ["There's {} in the way".format(obj_name)]

        elif error_code == ActionErrorCode.NOT_HOLDING:
            return ["I'm not holding anything"]


    def post_processed(self) -> 'Action':
        """
        :return: a post processed version of the action. Useful for changing the action into another form ready to
                 be sent to the game.
        """
        return self

    @classmethod
    def partial_response(cls) -> str:
        """
        :return: a question asking the player to give more information about this type they are trying to make.
        """
        raise NotImplementedError


class Stop(Action):
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
