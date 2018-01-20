from abc import ABC
from enum import Enum
from parser import *
from descriptor import *


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


class Location(ABC, SpeechParsable):
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

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        """
        :return: a descriptor which gives a high response for absolute locations, e.g. room 21.
        """
        return AllOf([WordMatch('room'), Number()])

    @classmethod
    def parse(cls, tokens: List[str]) -> 'Absolute':
        room_num = nltk_first_tagged('CD', tokens)
        return Absolute('room ' + str(room_num))


class Positional(Location):
    """
    The location of an object, out of many, relative to the player. E.g. the third door on the left.
    """

    position: int         # e.g. third
    object_name: str      # e.g. door
    direction: Direction  # e.g. on the right

    def __init__(self, position: int, object_name: str, direction: Direction):
        self.position = position
        self.object_name = object_name
        self.direction = direction

    def __str__(self):
        return '{} {} {}'.format(self.position, self.object_name, self.direction)

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        """
        :return: a descriptor which gives a high response for positional locations, e.g. third door on the left.
        """
        direction_words = ['left', 'right', 'behind', 'front']
        directions = OneOf(WordMatch.list_from_words(direction_words))
        you = OneOf(WordMatch.list_from_words(['you', 'your']))

        return And([Contextual(), WordTag('NN'), directions, you])

    @classmethod
    def parse(cls, tokens: List[str]) -> 'Positional':
        direction_possibilities = {
            'left': Direction.LEFT,
            'right': Direction.RIGHT,
            'behind': Direction.BACKWARDS,
            'front': Direction.FORWARDS
        }
        direction = parse_one_of(direction_possibilities, tokens) or Direction.FORWARDS
        position = parse_positional(tokens) or 0
        object_name = parse_object_name(tokens) or 'door'

        return Positional(position, object_name, direction)


class Directional(Location):
    """
    Directional locations relative to the player, e.g. forwards 10 meters.
    """

    direction: Direction

    def __init__(self, direction: Direction):
        self.direction = direction

    def __str__(self):
        return str(self.direction)

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        """
        :return: a descriptor which produces a high response for directions, e.g. forwards, backwards.
        """
        directions = [
            'forwards',
            'backwards',
            'forward',
            'backward'
        ]
        return OneOf(WordMatch.list_from_words(directions))

    @classmethod
    def parse(cls, tokens: List[str]) -> 'Directional':
        direction_possibilities = {
            'forwards': Direction.FORWARDS,
            'forward': Direction.FORWARDS,
            'backwards': Direction.BACKWARDS,
            'backward': Direction.BACKWARDS
        }

        direction = parse_one_of(direction_possibilities, tokens) or Direction.FORWARDS

        return Directional(direction)


class Stairs(Location):
    """
    A location up or downstairs from the current location of the player.
    """

    direction: FloorDirection

    def __init__(self, direction: FloorDirection):
        self.direction = direction

    def __str__(self):
        return '{} the stairs'.format(self.direction)

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        """
        :return: a descriptor which produces a high response for stairs, e.g. go upstairs.
        """
        # Either 'go up the stairs' or 'go down the stairs'
        up_down = OneOf(WordMatch.list_from_words(['up', 'down']))
        up_down_stairs = And([up_down, WordMatch('stairs')])

        # Either 'go upstairs' or `go downstairs'
        up_down_stairs_compound = OneOf(WordMatch.list_from_words(['upstairs', 'downstairs']))

        return OneOf([up_down_stairs, up_down_stairs_compound])

    @classmethod
    def parse(cls, tokens: List[str]) -> 'Stairs':
        direction_possibilities = {
            'up': FloorDirection.UP,
            'upstairs': FloorDirection.UP,
            'down': FloorDirection.DOWN,
            'downstairs': FloorDirection.DOWN
        }

        direction = parse_one_of(direction_possibilities, tokens) or FloorDirection.UP

        return Stairs(direction)


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

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        """
        :return: a descriptor which produces a high response for going behind an object, e.g. go behind the sofa.
        """
        return AllOf([WordMatch('behind'), WordTag('NN')])

    @classmethod
    def parse(cls, tokens: List[str]) -> 'Behind':
        object_name = parse_object_name(tokens) or 'desk'
        return Behind(object_name)
