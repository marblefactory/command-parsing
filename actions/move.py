from actions.action import Action, GameResponse, Composite
from actions.location import Location, MoveDirection, ObjectRelativeDirection, Absolute
from utils import PartialClassMixin
from typing import Optional, List


class Speed:
    SLOW = 'slow'
    NORMAL = 'normal'
    FAST = 'fast'


class Stance:
    CROUCH = 'crouch'
    STAND = 'stand'


class Turn(Action):
    """
    Tells the spy to turn to a particular direction.
    """

    direction: MoveDirection

    def __init__(self, direction: MoveDirection):
        self.direction = direction

    def __str__(self):
        return 'turn {}'.format(self.direction)


class ChangeStance(Action):
    """
    Tells the spy to change their stance.
    """

    stance: Stance

    def __init__(self, stance: Stance):
        self.stance = stance

    def __str__(self):
        return 'change stance to {}'.format(self.stance)


class ChangeSpeed(Action):
    """
    Tells the spy to change the speed they're performing their current movement at.
    """

    speed: Speed

    def __init__(self, speed: Speed):
        self.speed = speed

    def __str__(self):
        return 'change speed to {}'.format(self.speed)


class Move(PartialClassMixin, Action):
    """
    Tells the spy to move to a location.
    """

    def __init__(self, speed: Speed, location: Location, stance: Optional[Stance]):
        """
        :param speed: the speed to move at.
        :param location: the location to move to.
        :param stance: the stance to move into for the move. If None, the spy remains in their current stance.
        """
        self.speed = speed
        self.location = location
        self.stance = stance

    def __str__(self):
        return 'go "{}" at "{}" speed while "{}"'.format(self.location, self.speed, self.stance or 'no change')

    def specific_positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :return: positive responses for the move action. Does not expect anything to be given from the game.
        """
        return [
            "Moving to that position",
            "On my way",
            "Going there now",
            'OK',
            'Affirmative'
        ]

    def post_processed(self) -> Action:
        """
        :return: if the move is to an absolute location, the spy should enter the room after. Therefore, a composite
                 action is created containing this move, and a through door action.
                 Otherwise, just this action is returned.
        """
        if isinstance(self.location, Absolute):
            if (not (self.location.place_name == 'basement' or self.location.place_name == 'ground')):
                return Composite([self, ThroughDoor(ObjectRelativeDirection.VICINITY)])
        return self

    @classmethod
    def partial_response(cls) -> str:
        """
        :return: a response for just being asked to 'go'.
        """
        return 'To where?'


class Hide(Action):
    """
    Tells the spy to hide behind an object. If no object is given, the spy will hide behind the closest object.
    """

    def __init__(self, object_name: Optional[str]):
        self.object_name = object_name

    def __str__(self):
        return 'hide behind {}'.format(self.object_name or 'closest')

    def specific_positive_responses(self, game_response: GameResponse) -> List[str]:
        if self.object_name:
            extra = ["They won't find me behind the {}".format(self.object_name)]
        else:
            extra = []

        return extra + [
            "They won't find me there",
            "No one will find me there"
        ]


class ThroughDoor(Action):
    """
    Tells the spy to open the nearest door and walk through it.
    """

    direction: ObjectRelativeDirection

    def __init__(self, direction: ObjectRelativeDirection):
        self.direction = direction

    def __str__(self):
        return 'through door on {}'.format(self.direction)


class LeaveRoom(Action):
    """
    Tells the spy to leave they room they are in.
    """
    def __str__(self):
        return 'leave the room'
