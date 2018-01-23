from actions.action import Action
from actions.location import ObjectRelativeDirection, Location


class ThroughDoor(Action):
    """
    Tells the spy to open the nearest door and walk through it.
    """
    def __str__(self):
        return 'through door'


class PickUp(Action):
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


class Throw(Action):
    """
    Tells the spy to throw whatever object they've picked up.
    """

    target: Location

    def __init__(self, target: Location):
        self.target = target

    def __str__(self):
        return 'throw to "{}"'.format(self.target)

