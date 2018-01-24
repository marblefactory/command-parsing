import json

from encoders.encode_location import *


def make_cpp_json(location_json):
    """
    :param location_json: the json dictionary representation a location.
    :return: the new jankey json to fit with the c++ side.
    """

    if 'name' in location_json:
        obj_name = location_json['name']
        del location_json['name']
    else:
        obj_name = 'no_object'

    return {
        'name': obj_name,
        'location': location_json
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
            'dest': make_cpp_json(json.loads(json.dumps(obj.location, cls=LocationEncoder))),
            'stance': obj.stance or 'no_change',
            'speed': obj.speed
        }
