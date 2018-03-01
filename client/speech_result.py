from typing import Any, Callable
from actions.action import Action
from speech.record import Recorder
from speech.transcribe import transcribe_file
from parsing.pre_processing import pre_process
from parsing.parse_action import action
from encoders.encode_action import ActionEncoder
from requests import Response
import json


class Result:
    """
    Represents a result to a computation involving speech processing.
    """
    def then(self, operation: Callable[[Any], 'Result']) -> 'Result':
        """
        :param operation: used to construct a new speech result from this result.
        :return: performs this computation, then uses the result to return another result to operation.
        """
        raise NotImplementedError

    def either(self, success: Callable[[Any], Any], failure: Callable[[str], Any]) -> Any:
        """
        :param success: the function called on the result if it is a success.
        :param failure: the function called on the result if it is a failure.
        :return: the result of the chosen function on this result.
        """
        if isinstance(self, Success):
            return success(self.value)
        elif isinstance(self, Failure):
            return failure(self.error_msg)

        raise RuntimeError('non-recognised result')


class Success(Result):
    """
    Represents a successful result of a computation involving speech processing.
    """
    def __init__(self, value: Any):
        """
        :param value: the result of the computation.
        """
        self.value = value

    def then(self, operation: Callable[[Any], Result]) -> Result:
        """
        :param operation: used to construct a new speech result from this result.
        :return: performs this computation, then uses the result to return another result to operation.
        """
        return operation(self.value)


class Failure(Result):
    """
    Represents a failed result of a computation involving speech processing.
    """
    def __init__(self, error_msg: str = None):
        """
        :param error_msg: the error message to speak to the user.
        """
        self.error_msg = error_msg

    def then(self, operation: Callable[[Any], Result]) -> Result:
        """
        :param operation: used to construct a new speech result from this result.
        :return: the error message contained in this failure result.
        """
        return Failure(self.error_msg)


def print_produce(post_message: str, value: Any) -> Result:
    """
    :param post_message: the message printed before the value.
    :return: prints the value, and returns a success result containing the value.
             This cannot fail.
    """
    print(post_message, value)
    return Success(value)


def record(filename: str) -> Result:
    """
    :return: the a result containing the filename of where the recorded audio was written.
             This cannot fail.
    """
    recorder = Recorder(sample_rate=41500)
    recorder.record()
    recorder.write(filename)

    return Success(filename)


def transcribe(fail_response: Callable[[], str], audio_filename: str) -> Result:
    """
    :param fail_response: function to create a failure response.
    :return: result of transcribing the speech in the audio file with the given name.
             This fails if no speech could be recognised in the audio file.
    """
    transcript = transcribe_file(audio_filename)

    if not transcript:
        return Failure(fail_response())

    return Success(transcript)


def parse_action(fail_response: Callable[[str], str], transcript: str) -> Result:
    """
    :param fail_response: function to create a failure response from the transcript.
    :return: result of parsing the speech transcript into actions.
             This fails if an action could not be parsed from the transcript.
    """
    words = pre_process(transcript)
    result = action().parse(words)

    success = lambda s: Success(s.parsed)
    partial = lambda p: Success(p.failed_parser)
    failure = lambda _: Failure(fail_response(transcript))

    return result.either(success, partial, failure)


def send_to_server(fail_response: Callable[[Action], str], post: Callable[[str], Response], parsed_action: Action) -> Result:
    """
    :param fail_response: function to create a fail response from the parsed action.
    :param post: takes the JSON string representing the action, and posts it to the server.
    :return: result of sending the action to the game to be performed. This fails if the game could not perform the
             action.
    """
    action_json = json.loads(json.dumps(parsed_action, cls=ActionEncoder))
    response = post(action_json)

    if response.status_code != 200:
        return Failure(fail_response(parsed_action))

    return Success(parsed_action.random_response())
