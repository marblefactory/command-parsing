from actions.action import Action
from actions.single_actions import single_actions
from parsing.parser import SpeechParsable, parse_user_speech
from parsing.descriptor import Descriptor, WordMatch, NoneOf
from utils import split_list
from typing import Optional, List


class Composite(Action):
    """
    An action made of multiple actions, e.g. go left then go right.
    """

    def __init__(self, actions: List[Action]):
        self.actions = actions

    def __str__(self):
        descriptions = [str(action) for action in self.actions]
        return ' then '.join(descriptions)

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        return WordMatch('then')

    @classmethod
    def parse(cls, tokens: List[str]) -> Optional['Composite']:
        all_action_tokens = split_list(tokens, 'then')

        actions = []
        for action_tokens in all_action_tokens:
            action = parse_user_speech(action_tokens, single_actions())
            if action is not None:
                actions.append(action)

        return Composite(actions)


class SingleActionParser(SpeechParsable):
    """
    Used to parse a single action, i.e. a non-composite action.
    """

    @classmethod
    def text_descriptor(cls) -> Descriptor:
        # If it is not a composite action it must be a single action.
        return NoneOf([Composite.text_descriptor()])

    @classmethod
    def parse(cls, tokens: List[str]) -> Optional[Action]:
        return parse_user_speech(tokens, single_actions())


s = 'place the rabbit on your head'
action = parse_user_speech(s.split(), [Composite, SingleActionParser])
print(action)