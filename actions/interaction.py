from actions.action import Action
from actions.location import ObjectRelativeDirection, Location
from typing import List


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

    @classmethod
    def partial_response(cls) -> str:
        """
        :return: a response for just being asked to 'pick up'.
        """
        return 'Pick-up what?'


class Throw(Action):
    """
    Tells the spy to throw whatever object they've picked up.
    """

    target: Location

    def __init__(self, target: Location):
        self.target = target

    def __str__(self):
        return 'throw to "{}"'.format(self.target)

    def specific_responses(self) -> List[str]:
        return [
            "I hope this distracts the guard",
            "I hope the guard falls for this"
        ]


class Hack(Action):
    """
    Tells the spy to hack an object.
    """

    object_name: str
    direction: ObjectRelativeDirection

    def __init__(self, object_name: str, direction: ObjectRelativeDirection):
        self.object_name = object_name
        self.direction = direction

    def __str__(self):
        return 'hack "{}" "{}"'.format(self.object_name, self.direction)

    def specific_responses(self) -> List[str]:
        return [
            "I'll make a GUI interface using Visual Basic, see if I can track an IP address",
            "I'll get you access to their mainframe",
            "You'll need to isolate the node and dump it on the other side of the router",
            "I'll plug the communicator into the {}".format(self.object_name),
            "I'll get you access to their {}".format(self.object_name)
        ]

    @classmethod
    def partial_response(cls) -> str:
        """
        :return: a response for just being asked to 'hack'.
        """
        return 'Hack what?'
