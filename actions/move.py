from actions.action import Action
from actions.location import Location
from typing import Optional


class Speed:
    SLOW = 'slow'
    NORMAL = 'normal'
    FAST = 'fast'


class Stance:
    CROUCH = 'crouch'
    STAND = 'stand'


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
