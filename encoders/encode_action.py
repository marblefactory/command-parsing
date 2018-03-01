import json
from actions.action import *
from actions.interaction import *
from actions.move import *
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
        encoders = {
            Stop: StopEncoder,
            Composite: CompositeEncoder,
            ThroughDoor: ThroughDoorEncoder,
            PickUp: PickUpEncoder,
            Throw: ThrowEncoder,
            Hack: HackEncoder,
            ChangeStance: ChangeStanceEncoder,
            ChangeSpeed: ChangeSpeedEncoder,
            Move: MoveEncoder,
            Turn: TurnEncoder,
            Hide: HideEncoder
        }

        encoder = encoders.get(type(obj)) or json.JSONEncoder

        return encoder.default(self, obj)
