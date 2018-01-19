from abc import ABC
from enum import Enum
import numpy as np


class Direction(Enum):
    """
    The different the directions that the user can use.
    """

    LEFT      = 0
    RIGHT     = 1
    BACKWARDS = 2
    FORWARDS  = 3


class FloorDirection(Enum):
    """
    The different ways the user can travel using the stairs.
    """

    UP   = 0
    DOWN = 1

class Location(ABC):
    """
    Base class for locations.
    """

    @classmethod
    def from_tensor_and_text(cls, tensor: np.ndarray, text:str):
        return Absolute()


class Absolute(Location):
    """
    Represents a unique location in the map.
    """
    pass


class Contextual(Location):
    """
    A narrow set of locations relative to the player, e.g. third door on your right.
    """

    direction: Direction # e.g. on the right
    num      : int       # e.g. 3rd (door)

    def __init__(self, direction: Direction = Direction.FORWARDS, num: int = 0):
        self.direction = direction
        self.num = num


class Directional(Location):
    """
    Directional locations relative to the player, e.g. forwards 10 meters
    """

    direction: Direction

    def __init__(self, direction: Direction):
        self.direction = direction


class Stairs(Location):
    """
    A location up or downstairs from the current location of the player.
    """

    direction: FloorDirection

    def __init__(self, direction: FloorDirection):
        self.direction = direction