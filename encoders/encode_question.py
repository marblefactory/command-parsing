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


class SeeObjectQuestionEncoder(json.JSONEncoder):
    """
    Encodes a SeeObjectQuestion.
    """
    def default(self, obj):
        return {
            'type': 'see_object_question',
            'object_name': obj.object_name
        }


class TimeRemainingQuestionEncoder(json.JSONEncoder):
    """
    Encodes a TimeRemaining question.
    """
    def default(self, obj):
        return {
            'type': 'time_remaining_question'
        }
