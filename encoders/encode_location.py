import json
from actions.location import *

class MoveDirectionEncoder(json.JSONEncoder):
    """
    Encodes a MoveDirection.

    Fields:
        'direction'    : The direction
    """
    def default(self, obj):
        return {
            'direction': obj
        }


class ObjectRelativeDirectionEncoder(json.JSONEncoder):
    """
    Encodes a ObjectRelativeDirection.

    Fields:
        'type'    : The type of action
    """
    def default(self, obj):
        return {
            'direction': obj
        }


class FloorDirectionEncoder(json.JSONEncoder):
    """
    Encodes a FloorDirection.
    """
    def default(self, obj):
        return {
            'direction': obj
        }


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
            'name':  obj.objext_name,
            'direction': json.loads(json.dumps(obj.direction, cls=MoveDirectionEncoder))
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
            'direction': json.loads(json.dumps(obj.direction, cls=MoveDirectionEncoder))
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
            'direction': json.loads(json.dumps(obj.direction, cls=FloorDirectionEncoder))
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


class LocationEncoder(json.JSONEncoder):
    """
    Encodes a ObjectRelativeDirection.

    Fields:
        'type'    : The type of action
    """
    def default(self, obj):
        if isinstance(obj, Absolute):
            return json.loads(json.dumps(obj, cls=AbsoluteEncoder))
        elif isinstance(obj, Positional):
            return json.loads(json.dumps(obj, cls=PositionalEncoder))
        elif isinstance(obj, Directional):
            return json.loads(json.dumps(obj, cls=DirectionalEncoder))
        elif isinstance(obj, Stairs):
            return json.loads(json.dumps(obj, cls=StairsEncoder))
        elif isinstance(obj, Behind):
            return json.loads(json.dumps(obj, cls=BehindEncoder))
        return json.JSONEncoder.default(self, obj)

