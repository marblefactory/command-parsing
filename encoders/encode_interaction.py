from encoders.encode_location import *


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


class ThrowAtGuardEncoder(json.JSONEncoder):
    """
    Encodes a ThrowAtGuard action.
    """
    def default(self, obj):
        return {
            'type': 'throw_at_guard',
            'direction': obj.direction
        }


class StrangleGuardEncoder(json.JSONEncoder):
    """
    Encodes a StrangleGuard action.
    """
    def default(self, obj):
        return {
            'type': 'strangle',
            'direction': obj.direction
        }


class AutoTakeOutGuardEncoder(json.JSONEncoder):
    """
    Encodes a AutoTakeOutGuard action.
    """
    def default(self, obj):
        return {
            'type': 'attack',
            'direction': obj.direction
        }


class DropEncoder(json.JSONEncoder):
    """
    Encodes a Drop action.
    """
    def default(self, obj):
        return {
            'type': 'drop'
        }


class HackEncoder(json.JSONEncoder):
    """
    Encodes a Hack action.
    """
    def default(self, obj):
        return {
            'type': 'hack',
            'hack_type': obj.object_type,
            'direction': obj.direction
        }


class PickpocketEncoder(json.JSONEncoder):
    """
    Encodes a Pickpocket action.
    """
    def default(self, obj):
        return {
            'type': 'pickpocket',
            'direction': obj.direction
        }


class DestroyGeneratorEncoder(json.JSONEncoder):
    """
    Encodes a DestroyGenerator action.
    """
    def default(self, obj):
        return {
            'type': 'destroy_generator'
        }
