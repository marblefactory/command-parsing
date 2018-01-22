
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

