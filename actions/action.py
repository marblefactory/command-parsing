from typing import List


class Action():
    """
    An action that the player can command the spy to make.
    """
    pass


class Stop(Action):
    """
    Tells the spy to stop whatever they're doing.
    """

    def __str__(self):
        return 'stop'


class Composite(Action):
    """
    An action made of multiple actions, e.g. go left then go right.
    """

    def __init__(self, actions: List[Action]):
        self.actions = actions

    def __str__(self):
        descriptions = [str(action) for action in self.actions]
        return ' then '.join(descriptions)
