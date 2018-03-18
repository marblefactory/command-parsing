from actions.action import Action, GameResponse
from typing import List


class InventoryContentsQuestion(Action):
    """
    An action to ask the spy what's in their inventory.
    """
    def positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :param game_response: the json response from the game. Expects this to contain a key named 'inventory_items'
                              which has a string value which is the name of the item the spy is carrying.
        :return:
        """
        # The items the spy is holding.
        item = game_response['inventory_item']
        return [
            "I'm holding a {}".format(item),
            "I've got a {}".format(item)
        ]


class LocationQuestion(Action):
    """
    An action to ask the spy where they are.
    """
    def positive_responses(self, game_response: GameResponse) -> List[str]:
        """
        :param game_response: the json response from the game. Expects this to contain a key named 'location'
                              which has a string value which is the name of the location of the spy.
        :return:
        """
        # The items the spy is holding.
        location = game_response['location']
        return [
            "I'm in {}".format(location)
        ]
