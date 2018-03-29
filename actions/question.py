from actions.action import Action, GameResponse
from utils import join_with_last
from typing import List
import inflect
from itertools import groupby

class Question(Action):
    """
    Base class for questions. Used to identify questions so they can be sent
    to a different handler in the game server.
    """
    pass


class InventoryContentsQuestion(Question):
    """
    An action to ask the spy what's in their inventory.
    """
    def __str__(self):
        return 'inventory contents question'

    def positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :param game_response: the json response from the game. Expects this to contain a key named 'inventory_items'
                              which has a string value which is the name of the item the spy is carrying.
        :return: a list of responses describing what the spy is holding.
        """
        # The items the spy is holding.
        item = game_response['inventory_item']
        return [
            "I'm holding a {}".format(item),
            "I've got a {}".format(item)
        ]


class LocationQuestion(Question):
    """
    An action to ask the spy where they are.
    """
    def __str__(self):
        return 'location question'

    def positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :param game_response: the json response from the game. Expects this to contain a key named 'location'
                              which has a string value which is the name of the location of the spy.
        :return: a list of responses describing the location of the spy.
        """
        # The items the spy is holding.
        location = game_response['location']
        return [
            "I'm in {}".format(location)
        ]


class GuardsQuestion(Question):
    """
    An action to ask the spy if they can see any guards.
    """
    def __str__(self):
        return 'guards question'

    def positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :param game_response: the json response from the game. Expects this to contain a key named 'num_guards'
                              which is an integer of the number of guards around the spy.
        :return: a list of responses describing the guards the spy can see.
        """
        num_guards = int(game_response['num_guards'])

        if num_guards == 0:
            return [
                "I can't see any at the moment",
                "No guards around here",
                "The coast is clear"
            ]

        elif num_guards == 1:
            return [
                "It's okay, there's only one nearby",
                "I can only see one guard",
                "There's one guard nearby"
            ]

        elif 1 < num_guards <= 5:
            return [
                "I can see {} guards".format(num_guards),
                "There are {} guards nearby".format(num_guards)
            ]

        else:
            return [
                "They're everywhere!",
                "There's a lot of guards",
                "I can see {} guards".format(num_guards),
            ]


class SurroundingsQuestion(Question):
    """
    An action to ask the spy what they can see around them.
    """
    def __str__(self):
        return 'surroundings question'

    def positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :param game_response: the json response from the game. Expects this to contain a key named 'surroundings'
                              which is a list of strings of objects around the spy.
        :return: a list of responses describing what the spy can see.
        """
        engine = inflect.engine()

        # The objects around the spy.
        objects = game_response['surroundings']

        # Group the objects into tuples containing their name and the number of times they were found around the spy.
        # Therefore the spy can say things like 'I can see a server and two cameras'.
        groups = [list(v) for k,v in groupby(objects)]

        # Returns the description of a group of objects, e.g. ['camera', 'camera'] goes to '2 cameras'.
        def make_description(group: List[str]) -> str:
            count = len(group)
            # Adds an 's' the name if there is more than 1.
            plural = engine.plural(text=group[0], count=count)
            # Adds 'a' or 'an' to the front of the names of the objects. Also gives the
            return engine.a(plural, count=count)

        descriptions = list(map(make_description, groups))
        # The descriptions join with commas, and an 'and' at the end.
        joined_descriptions = join_with_last(descriptions, ', ', ' and ')

        return [
            "I can see {}".format(joined_descriptions),
            "There's {}".format(joined_descriptions)
        ]


class SeeObjectQuestion(Question):
    """
    An action to ask the spy whether they can see a specific object, e.g. 'Can you see a rock near you?'
    """

    def __init__(self, object_name: str):
        """
        :param object_name: the name of the object for the spy to look for.
        """
        self.object_name = object_name

    def __str__(self):
        return 'see object question'

    def positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :return: responses that confirm that the spy can see the requested object.
        """
        return [
            "There's a {} near me".format(self.object_name),
            "I can see a {}".format(self.object_name),
            "I can",
            "Yes"
        ]

    def negative_responses(self) -> List[str]:
        """
        :return: responses that tell the player the requested object is not near the spy.
        """
        return [
            "I can't see any",
            "No",
            "Umm, I can't see any here",
            "I'm afraid not"
        ]
