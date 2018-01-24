from equatable import EquatableMixin


class MoveDirection:
    """
    The different the directions that the user can travel in on a single floor.
    """

    LEFT = 'left'
    RIGHT = 'right'
    BACKWARDS = 'backwards'
    FORWARDS = 'forwards'


class ObjectRelativeDirection(MoveDirection):
    """
    The different directions that an object can be in compared to the position of the spy.
    """

    # For finding an object within a vicinity of the spy.
    VICINITY = 'vicinity'


class FloorDirection:
    """
    The different ways the user can travel using the stairs.
    """

    UP = 'up'
    DOWN = 'down'


class Location(EquatableMixin):
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

    position: int             # e.g. third
    object_name: str          # e.g. door
    direction: MoveDirection  # e.g. on the right

    def __init__(self,  object_name: str, position: int, direction: ObjectRelativeDirection):
        self.position = position
        self.object_name = object_name
        self.direction = direction

    def __str__(self):
        return '{} {} {}'.format(self.position, self.object_name, self.direction)


class Directional(Location):
    """
    Directional locations relative to the player, e.g. forwards 10 meters.
    """

    direction: MoveDirection

    def __init__(self, direction: MoveDirection):
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
    A location behind an object.
    """

    object_name: str

    def __init__(self, object_name: str):
        self.object_name = object_name

    def __str__(self):
        return 'behind {}'.format(self.object_name)
