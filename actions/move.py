from actions.action import Action
from actions.location import Location, MoveDirection
from typing import Optional
from typing import List


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
        return self.stance


class Move(Action):
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

    def specific_responses(self) -> List[str]:
        return ['moving to that position', 'on my way']


class Hide(Action):
    """
    Tells the spy to hide behind an object. If no object is given, the spy will hide behind the closest object.
    """

    def __init__(self, object_name: Optional[str]):
        self.object_name = object_name

    def __str__(self):
        return 'hide behind {}'.format(self.object_name or 'closest')
