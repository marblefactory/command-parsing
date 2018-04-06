import json
from actions.location import *


class AbsoluteEncoder(json.JSONEncoder):
    """
    Encodes a Absolute location.
    """
    def default(self, obj):
        return {
            'type': 'absolute',
            'name': obj.place_name
        }


class PositionalEncoder(json.JSONEncoder):
    """
    Encodes a Positional location.

    Fields:
        'type'    : The type of action
        'index'   : 0 -> 1st
        'name'    : The name of the object
        'direction': the direction of the object
    """
    def default(self, obj):
        return {
            'type': 'positional',
            'index': obj.position,
            'name':  obj.object_name,
            'direction': obj.direction
        }


class DirectionalEncoder(json.JSONEncoder):
    """
    Encodes a Positional location.

    Fields:
        'type'    : The type of action
        'direction': the direction of the object
    """
    def default(self, obj):
        return {
            'type': 'directional',
            'direction': obj.direction,
            'distance': obj.distance
        }


class StairsEncoder(json.JSONEncoder):
    """
    Encodes a Positional location.

    Fields:
        'type'    : The type of action
        'direction': the direction of the object
    """
    def default(self, obj):
        return {
            'type': 'stairs',
            'direction': obj.direction or 'none'
        }


class BehindEncoder(json.JSONEncoder):
    """
    Encodes a Positional location.

    Fields:
        'type'    : The type of action
        'name'    : The name of the object to go behind
    """
    def default(self, obj):
        return {
            'type': 'behind',
            'name': obj.object_name
        }


class EndOfEncoder(json.JSONEncoder):
    """
    Encodes an EndOf location.

    Fields:
        'type': The type of action.
        'name': The name of the object to go to the end of.
    """
    def default(self, obj):
        return {
            'type': 'end_of',
            'name': obj.object_name
        }


class LocationEncoder(json.JSONEncoder):
    """
    Encodes a ObjectRelativeDirection.

    Fields:
        'type'    : The type of action
    """
    def default(self, obj):
        if isinstance(obj, Absolute):
            encoder = AbsoluteEncoder
        elif isinstance(obj, Positional):
            encoder = PositionalEncoder
        elif isinstance(obj, Directional):
            encoder = DirectionalEncoder
        elif isinstance(obj, Stairs):
            encoder = StairsEncoder
        elif isinstance(obj, Behind):
            encoder = BehindEncoder
        elif isinstance(obj, EndOf):
            encoder = EndOfEncoder
        else:
            raise RuntimeError('unexpected location type when encoding')

        return encoder.default(self, obj)
