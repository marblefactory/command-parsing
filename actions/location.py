from abc import ABC
from enum import Enum


class Direction(Enum):
    """
    The different the directions that the user can travel in on a single floor.
    """

    LEFT = 0
    RIGHT = 1
    BACKWARDS = 2
    FORWARDS = 3

    def __str__(self):
        if self == Direction.FORWARDS:
            return 'forwards'
        elif self == Direction.BACKWARDS:
            return 'backwards'
        elif self == Direction.LEFT:
            return 'left'
        elif self == Direction.RIGHT:
            return 'right'


class FloorDirection(Enum):
    """
    The different ways the user can travel using the stairs.
    """

    UP = 0
    DOWN = 1

    def __str__(self):
        if self == FloorDirection.UP:
            return 'up'
        return 'down'


class Location(ABC):
    """
    Base class for locations.
    """
    pass


class Absolute(Location):
    """
    Represents the location of a unique object in the map.
    """

    place_name: str

    def __init__(self, place_name: str):
        """
        :param place_name: the name of the unique location in the map, e.g room 21.
        """
        self.place_name = place_name

    def __str__(self):
        return self.place_name


class Positional(Location):
    """
    The location of an object, out of many, relative to the player. E.g. the third door on the left.
    """

    position: int         # e.g. third
    object_name: str      # e.g. door
    direction: Direction  # e.g. on the right

    def __init__(self,  object_name: str, position: int, direction: Direction):
        self.position = position
        self.object_name = object_name
        self.direction = direction

    def __str__(self):
        return '{} {} {}'.format(self.position, self.object_name, self.direction)


class Directional(Location):
    """
    Directional locations relative to the player, e.g. forwards 10 meters.
    """

    direction: Direction

    def __init__(self, direction: Direction):
        self.direction = direction

    def __str__(self):
        return str(self.direction)


class Stairs(Location):
    """
    A location up or downstairs from the current location of the player.
    """

    direction: FloorDirection

    def __init__(self, direction: FloorDirection):
        self.direction = direction

    def __str__(self):
        return '{} the stairs'.format(self.direction)


class Behind(Location):
    """
    A location behind an object, e.g. hide behind the desk.
    """

    object_name: str

    def __init__(self, object_name: str):
        """
        :param object_name: the name of the object to move behind.
        """
        self.object_name = object_name

    def __str__(self):
        return 'behind {}'.format(self.object_name)
