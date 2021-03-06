from actions.action import PostProcessed
from typing import List
from equatable import EquatableMixin


class Conversation(PostProcessed, EquatableMixin):
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


class WhatName(Conversation):
    """
    The player asked what the spy's name is.
    """
    def responses(self) -> List[str]:
        return [
            "Ethan Hunt"
        ]


class WhoAreYou(Conversation):
    """
    The player asked who the spy was.
    """
    def responses(self) -> List[str]:
        return [
            "Me? ... I know who I am!"
        ]


class Obscenity(Conversation):
    """
    The player swore at the spy.
    """
    def responses(self) -> List[str]:
        return [
            "I don't appreciate that",
            "Calm the fuck down"
        ]


class Repeat(Conversation):
    """
    The player asked the spy to repeat something.
    """
    def __init__(self, words: List[str]):
        self.words = words

    def responses(self) -> List[str]:
        return [' '.join(self.words)]

