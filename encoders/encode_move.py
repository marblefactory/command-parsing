import json

from encoders.encode_location import *


class StanceEncoder(json.JSONEncoder):
    """
    Encodes a Stance.

    Fields:
        'stance'  : The stance
    """

    def default(self, obj):
        return {
            'stance': obj
        }


class SpeedEncoder(json.JSONEncoder):
    """
    Encodes a Speed.

    Fields:
        'stance'  : The stance
    """

    def default(self, obj):
        return {
            'stance': obj
        }


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
            'stance': json.loads(json.dumps(obj.stance, cls=StanceEncoder))
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
            'stance': json.loads(json.dumps(obj.stance, cls=StanceEncoder)),
            'speed': json.loads(json.dumps(obj.speed, cls=SpeedEncoder))
        }
