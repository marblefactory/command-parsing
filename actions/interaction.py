from actions.action import Action
from actions.location import ObjectRelativeDirection, Location


class ThroughDoor(Action):
    """
    Tells the spy to open the nearest door and walk through it.
    """
    pass


class PickUp(Action):
    """
    Tells the spy to pick up an object, e.g. pick up the rock on your left.
    """

    object_name: str
    direction: ObjectRelativeDirection

    def __init__(self, object_name: str, direction: ObjectRelativeDirection):
        self.object_name = object_name
        self.direction = direction


class Throw(Action):
    """
    Tells the spy to throw whatever object they've picked up.
    """

    target: Location

    def __init__(self, target: Location):
        self.target = target

