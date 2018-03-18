import json


class InventoryContentsQuestionEncoder(json.JSONEncoder):
    """
    Encodes an InventoryContentsQuestion action.
    """
    def default(self, obj):
        return {
            'type': 'inventory_question'
        }


class LocationQuestionEncoder(json.JSONEncoder):
    """
    Encodes an LocationQuestion action.
    """
    def default(self, obj):
        return {
            'type': 'location_question'
        }
