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


class GuardsQuestionEncoder(json.JSONEncoder):
    """
    Encodes a GuardQuestion.
    """
    def default(self, obj):
        return {
            'type': 'guards_question'
        }

class SurroundingsQuestionEncoder(json.JSONEncoder):
    """
    Encodes a SurroundingsQuestion.
    """
    def default(self, obj):
        return {
            'type': 'surroundings_question'
        }
