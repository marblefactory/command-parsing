from typing import Any, Callable


class SpeechResult:
    """
    Represents a result to a computation involving speech processing.
    """

    def then(self, operation: Callable[[Any], 'SpeechResult']) -> 'SpeechResult':
        """
        :param operation: used to construct a new speech result from this result.
        :return: performs this computation, then uses the result to return another result to operation.
        """
        raise NotImplementedError


class SpeechSuccess(SpeechResult):
    """
    Represents a successful result of a computation involving speech processing.
    """

    def __init__(self, value: Any):
        """
        :param value: the result of the computation.
        """
        self.value = value

    def then(self, operation: Callable[[Any], 'SpeechResult']) -> SpeechResult:
        """
        :param operation: used to construct a new speech result from this result.
        :return: performs this computation, then uses the result to return another result to operation.
        """
        return operation(self.value)


class SpeechFailure(SpeechResult):
    """
    Represents a failed result of a computation involving speech processing.
    """

    def __init__(self, speech_err_message: str):
        """
        :param speech_err_message: the error message to speak to the user.
        """
        self.speech_err_message = speech_err_message

    def then(self, operation: Callable[[Any], 'SpeechResult']) -> SpeechResult:
        """
        :param operation: used to construct a new speech result from this result.
        :return: the error message contained in this failure result.
        """
        return SpeechFailure(self.speech_err_message)
