from actions.action import Action
from actions.location import Location
from enum import Enum


class Speed(Enum):
    SLOW = 0
    NORMAL = 1
    FAST = 2

    def __str__(self):
        if self == Speed.SLOW:
            return 'slow'
        elif self == Speed.NORMAL:
            return 'normal'
        else:
            return 'fast'


class Stance(Enum):
    CROUCH = 0
    STAND = 1

    def __str__(self):
        if self == Stance.CROUCH:
            return 'crouched'
        else:
            return 'standing'


class Move(Action):
    """
    An action that tells the spy to move to a location.
    """

    def __init__(self, speed: Speed, stance: Stance, location: Location):
        self.speed = speed
        self.stance = stance
        self.location = location

    def __str__(self):
        return 'go to {} at {} speed while {}'.format(self.location, self.speed, self.stance)
