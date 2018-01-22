from typing import List


class Composite(Action):
    """
    An action made of multiple actions, e.g. go left then go right.
    """

    def __init__(self, actions: List[Action]):
        self.actions = actions

    def __str__(self):
        descriptions = [str(action) for action in self.actions]
        return ' then '.join(descriptions)
