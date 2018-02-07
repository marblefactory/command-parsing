import json
from encoders.encode_location import *


class ThroughDoorEncoder(json.JSONEncoder):
    """
    Encodes a ThroughDoor action.

    Fields:
        'type'    : The type of action
    """
    def default(self, obj):
        return {
            'type': 'opendoor'
        }


class PickUpEncoder(json.JSONEncoder):
    """
    Encodes a PickUp action.

    Fields:
        'type'    : The type of action
    """

    def default(self, obj):
        return {
            'type': 'pickup',
            'name': obj.object_name,
            'direction': obj.direction
        }


class ThrowEncoder(json.JSONEncoder):
    """
    Encodes a Throw action.

    Fields:
        'type'    : The type of action
    """

    def default(self, obj):
        return {
            'type': 'throw',
            'location': json.loads(json.dumps(obj.target, cls=LocationEncoder))
        }


class HackEncoder(json.JSONEncoder):
    """
    Encodes a Hack action.
    """

    def default(self, obj):
        return {
            'type': 'hack',
            'name': obj.object_name,
            'direction': obj.direction
        }