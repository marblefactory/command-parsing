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

    def map_failure(self, transform: Callable[[str], str]) -> 'Result':
        """
        :param transform: used to generate a new failure from the message inside a failure.
        :return: has no effect on success results. However, replaces the error message inside a failure with the
                 string returned by transform.
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

    def map_failure(self, transform: Callable[[str], str]) -> Result:
        """
        :param transform: used to generate a new failure from the message inside a failure.
        :return: this success result, i.e. it has no effect.
        """
        return Success(self.value)


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

    def map_failure(self, transform: Callable[[str], str]) -> Result:
        """
        :param transform: used to generate a new failure from the message inside a failure.
        :return: this failure result where the the message has been replaced with the value of transform.
        """
        return Failure(transform(self.error_msg))


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


def transcribe(audio_filename: str) -> Result:
    """
    :return: result of transcribing the speech in the audio file with the given name.
             This fails if no speech could be recognised in the audio file.
    """
    transcript = transcribe_file(audio_filename)

    print(transcript)

    if not transcript:
        return Failure()

    return Success(transcript)


def parse_action(transcript: str) -> Result:
    """
    :return: result of parsing the speech transcript into actions.
             This fails if an action could not be parsed from the transcript.
    """
    words = pre_process(transcript)
    result = action().parse(words)

    if not result:
        print("FAILED ACTION")
        return Failure(transcript)

    return Success(result.parsed)


def send_to_server(post: Callable[[str], Response], parsed_action: Action) -> Result:
    """
    :param post: takes the JSON string representing the action, and posts it to the server.
    :return: result of sending the action to the game to be performed. This fails if the game could not perform the
             action.
    """
    action_json = json.loads(json.dumps(parsed_action, cls=ActionEncoder))
    response = post(action_json)

    print(response)

    if response.status_code != 200:
        return Failure()

    return Success(parsed_action.random_response())
