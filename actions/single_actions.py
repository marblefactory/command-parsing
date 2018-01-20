from actions.move import Move
from actions.action import Action, Stop
from typing import List, Type


def single_actions() -> List[Type[Action]]:
    """
    :return: all the possible non-composite actions.
    """
    return [Stop, Move]
