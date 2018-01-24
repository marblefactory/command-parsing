import json

from encoders.encode_location import *


class ChangeStanceEncoder(json.JSONEncoder):
    """
    Encodes a ChangeStance action.

    Fields:
        'type'    : The type of action
        'stance'  : The stance
    """

    def default(self, obj):
        return {
            'type': 'change_stance',
            'stance': obj.stance
        }


class MoveEncoder(json.JSONEncoder):
    """
    Encodes a ChangeStance action.

    Fields:
        'type'    : The type of action
        'dest'    : The location
        'stance'  : The stance
        'speed'   : The speed of travel
    """

    def default(self, obj):
        return {
            'type': 'move',
            'dest': json.loads(json.dumps(obj.location, cls=LocationEncoder)),
            'stance': obj.stance or 'no_change',
            'speed': obj.speed
        }
