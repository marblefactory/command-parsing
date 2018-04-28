from typing import List


class Conversation:
    """
    Represents a response that does not need to be sent to the game server.
    """
    def responses(self) -> List[str]:
        """
        :return:
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
