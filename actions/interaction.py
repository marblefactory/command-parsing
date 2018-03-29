from actions.action import Action, ActionDefaultPositiveResponseMixin, GameResponse
from actions.location import ObjectRelativeDirection, Location
from utils import PartialClassMixin
from typing import List


class PickUp(ActionDefaultPositiveResponseMixin, PartialClassMixin, Action):
    """
    Tells the spy to pick up an object, e.g. pick up the rock on your left.
    """

    object_name: str
    direction: ObjectRelativeDirection

    def __init__(self, object_name: str, direction: ObjectRelativeDirection):
        self.object_name = object_name
        self.direction = direction

    def __str__(self):
        return 'pick up "{}" "{}"'.format(self.object_name, self.direction)

    @classmethod
    def partial_response(cls) -> str:
        """
        :return: a response for just being asked to 'pick up'.
        """
        return 'Pick-up what?'


class Throw(ActionDefaultPositiveResponseMixin, Action):
    """
    Tells the spy to throw whatever object they've picked up.
    """

    target: Location

    def __init__(self, target: Location):
        self.target = target

    def __str__(self):
        return 'throw to "{}"'.format(self.target)

    def specific_positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :return: positive responses for the throw action. Does not expect anything to be given from the game.
        """
        return [
            "I hope this distracts the guard",
            "I hope the guard falls for this"
        ]


class ThrowAtGuard(ActionDefaultPositiveResponseMixin, Action):
    """
    Tells the spy to throw whatever they've picked up at a guard.
    """

    # The direction of the guard to throw something at, relative to the spy.
    direction: ObjectRelativeDirection

    def __init__(self, direction: ObjectRelativeDirection):
        self.direction = direction

    def __str__(self):
        return 'throw at guard'

    def specific_positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :return: positive responses for the throw action. Does not expect anything to be given from the game.
        """
        return [
            "Take that!",
            "I hope this hurts!"
        ]


class Drop(ActionDefaultPositiveResponseMixin, Action):
    """
    Tells the spy to drop the object they're holding.
    """
    def __str__(self):
        return 'drop'


class HackableType:
    """
    The types of objects which can be hacked.
    """
    CAMERA = 'camera'
    TERMINAL = 'terminal'


class Hack(ActionDefaultPositiveResponseMixin, PartialClassMixin, Action):
    """
    Tells the spy to hack an object.
    """

    # Whether to hack a camera or terminal.
    object_type: HackableType
    # The specific name of the object to hack, e.g. hacking a server equates to hacking a terminal.
    object_name: str
    # The direction, relative to the spy, of the object.
    direction: ObjectRelativeDirection

    def __init__(self, object_type: HackableType, object_name: str, direction: ObjectRelativeDirection):
        self.object_type = object_type
        self.object_name = object_name
        self.direction = direction

    def __str__(self):
        return 'hack "{}" ({}) "{}"'.format(self.object_name, self.object_type, self.direction)

    def specific_positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :return: positive responses for the hack action. Does not expect anything to be given from the game.
        """
        return [
            "I'll make a GUI interface using Visual Basic, see if I can track an IP address",
            "I'll get you access to their mainframe",
            "I'll need to isolate the node and dump it on the other side of the router",
            "I'll plug the communicator into the {}".format(self.object_name),
            "I'll get you access to their {}".format(self.object_name)
        ]

    @classmethod
    def partial_response(cls) -> str:
        """
        :return: a response for just being asked to 'hack'.
        """
        return 'Hack what?'


class Pickpocket(ActionDefaultPositiveResponseMixin, Action):
    """
    Tells the spy to pickpocket a guard.
    """

    # The direction of the guard relative to the spy.
    direction: ObjectRelativeDirection

    def __init__(self, direction: ObjectRelativeDirection):
        self.direction = direction

    def __str__(self):
        return 'pickpocket the guard on {}'.format(self.direction)
