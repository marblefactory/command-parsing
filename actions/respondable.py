from typing import List


class Respondable:
    """
    A type to which a response can be formulated. For example, a reply to `go forward` could be 'affirmative', 'okay',
    'going there', etc
    """
    def responses(self) -> List[str]:
        """
        :return: all the possible responses.
        """
        raise NotImplementedError
