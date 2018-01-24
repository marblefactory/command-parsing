import json
from actions.action import *
from actions.interaction import *
from actions.move import *
from encoders.encode_location import *
from encoders.encode_interaction import *
from encoders.encode_move import *



class StopEncoder(json.JSONEncoder):
    """
    Encodes a Stop action.

    Fields:
        'type'    : The type of action
    """
    def default(self, obj):
        return {
            'type': 'stop'
        }


class CompositeEncoder(json.JSONEncoder):
    """
    Encodes a composite action.

    Fields:
        'type'    : The type of action
        'actions' : A list of encoded actions
    """
    def default(self, obj):
        return {
            'type': 'composite',
            'actions': [json.loads(json.dumps(action, cls=ActionEncoder)) for action in obj.actions]
        }


class ActionEncoder(json.JSONEncoder):
    """
    Encodes an action into JSON for sending
    """
    def default(self, obj):
        if isinstance(obj, Stop):
            return json.loads(json.dumps(obj, cls=StopEncoder))
        elif isinstance(obj, Composite):
            return json.loads(json.dumps(obj, cls=CompositeEncoder))
        elif isinstance(obj, ThroughDoor):
            return json.loads(json.dumps(obj, cls=ThroughDoorEncoder))
        elif isinstance(obj, PickUp):
            return json.loads(json.dumps(obj, cls=PickUpEncoder))
        elif isinstance(obj, Throw):
            return json.loads(json.dumps(obj, cls=ThrowEncoder))
        elif isinstance(obj, ChangeStance):
            return json.loads(json.dumps(obj, cls=ChangeStanceEncoder))
        elif isinstance(obj, Move):
            return json.loads(json.dumps(obj, cls=MoveEncoder))
        return json.JSONEncoder.default(self, obj)








