from typing import List
from equatable import EquatableMixin


class Conversation(EquatableMixin):
    """
    Represents a response that does not need to be sent to the game server.
    """
    def responses(self) -> List[str]:
        """
        :return: default responses for if no action was parsed.
        """
        raise NotImplementedError


class Greeting(Conversation):
    """
    The player said a greeting to the spy, e.g. Hello.
    """
    def responses(self) -> List[str]:
        return [
            "Hello",
            "Hi",
            "Hi, but can we get on with the mission?",
            "There's no time for pleasantries! The fate of the world is at stake!"
        ]


class DefaultConversation(Conversation):
    """
    Parsed if no other actions or conversations were parsed.
    """
    def responses(self) -> List[str]:
        return [
            "I can't do that",
            "I don't know what you mean",
            "What exactly do you mean by that",
            "That's not part of my training"
        ]
