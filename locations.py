from abc import ABC
from enum import Enum
import numpy as np


class Direction(Enum):
    """
    The different the directions that the user can travel in on a single floor.
    """

    LEFT = 0
    RIGHT = 1
    BACKWARDS = 2
    FORWARDS = 3


class FloorDirection(Enum):
    """
    The different ways the user can travel using the stairs.
    """

    UP = 0
    DOWN = 1


class Location(ABC):
    """
    Base class for locations.
    """

    @classmethod
    def from_tensor_and_text(cls, tensor: np.ndarray, text: str):
        return Absolute()


class Absolute(Location):
    """
    Represents the location of a unique object in the map.
    """

    @classmethod
    def from_tensor_and_text(cls, tensor: np.ndarray, text: str):
        pass


class Positional(Location):
    """
    The location of an object, out of many, relative to the player. E.g. the third door on the left.
    """

    direction: Direction  # e.g. on the right
    position: int         # e.g. 3rd (door)

    def __init__(self, direction: Direction, position: int):
        self.direction = direction
        self.position = position


class Directional(Location):
    """
    Directional locations relative to the player, e.g. forwards 10 meters.
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


class Behind(Location):
    """
    A location behind an object, e.g. hide behind the desk.
    """
    pass
