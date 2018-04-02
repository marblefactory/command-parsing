from actions.action import *
from actions.interaction import *
from actions.move import *
from actions.question import *

from encoders.encode_interaction import *
from encoders.encode_move import *
from encoders.encode_question import *


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
            encoder = StopEncoder
        elif isinstance(obj, Composite):
            encoder = CompositeEncoder
        elif isinstance(obj, ThroughDoor):
            encoder = ThroughDoorEncoder
        elif isinstance(obj, PickUp):
            encoder = PickUpEncoder
        elif isinstance(obj, Throw):
            encoder = ThrowEncoder
        elif isinstance(obj, Hack):
            encoder = HackEncoder
        elif isinstance(obj, ChangeStance):
            encoder = ChangeStanceEncoder
        elif isinstance(obj, ChangeSpeed):
            encoder = ChangeSpeedEncoder
        elif isinstance(obj, Move):
            encoder = MoveEncoder
        elif isinstance(obj, Turn):
            encoder = TurnEncoder
        elif isinstance(obj, Hide):
            encoder = HideEncoder
        elif isinstance(obj, LeaveRoom):
            encoder = LeaveRoomEncoder
        elif isinstance(obj, InventoryContentsQuestion):
            encoder = InventoryContentsQuestionEncoder
        elif isinstance(obj, LocationQuestion):
            encoder = LocationQuestionEncoder
        elif isinstance(obj, GuardsQuestion):
            encoder = GuardsQuestionEncoder
        elif isinstance(obj, SurroundingsQuestion):
            encoder = SurroundingsQuestionEncoder
        elif isinstance(obj, Drop):
            encoder = DropEncoder
        elif isinstance(obj, Pickpocket):
            encoder = PickpocketEncoder
        elif isinstance(obj, ThrowAtGuard):
            encoder = ThrowAtGuardEncoder
        elif isinstance(obj, SeeObjectQuestion):
            encoder = SeeObjectQuestionEncoder
        elif isinstance(obj, DestroyGenerator):
            encoder = DestroyGeneratorEncoder
        elif isinstance(obj, TakeOutGuard):
            encoder = TakeOutGuardEncoder
        elif isinstance(obj, TimeRemainingQuestion):
            encoder = TimeRemainingQuestionEncoder
        else:
            raise RuntimeError('unexpected action type when encoding')

        return encoder.default(self, obj)
