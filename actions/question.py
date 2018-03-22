from actions.action import Action, GameResponse
from typing import List


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
