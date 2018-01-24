import json
from actions.action import *

class StopEncoder(json.JSONEncoder):
    """
    TOOO: Document
    """
    def default(self, obj):
        return {
            'type': 'stop',
        }



class ActionEncoder(json.JSONEncoder):
    """
    TOOO: Document
    """
    def default(self, obj):
        if isinstance(obj, Stop):
            return json.loads(json.dumps(obj, cls=StopEncoder))
        elif isinstance(obj, Composite):
            return json.loads(json.dumps(obj, cls=CompositeEncoder))
        return json.JSONEncoder.default(self, obj)



        return new_json





