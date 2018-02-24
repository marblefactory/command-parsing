from functools import partial
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from client.formulate_result import record, transcribe, parse_action, send_to_server
from client.speech_result import SpeechSuccess, SpeechFailure
from speech.voice import say


class Client:
    """
    Holds data used to formulate responses and send data to the server.
    """

    def _get_chatbot(self, spy_name: str) -> ChatBot:
        chatbot = ChatBot(spy_name)
        chatbot.set_trainer(ChatterBotCorpusTrainer)
        chatbot.train("chatterbot.corpus.english")

        return chatbot

    def __init__(self,
                 server_addr: str,
                 audio_filename: str,
                 transcribe_fail_responses_filename: str,
                 spy_name: str,
                 server_fail_responses_filename: str):
        """
        :server_addr: the address of the game server.
        :param audio_filename: the name of the audio file used to store recorded speech.
        :param transcribe_fail_responses_filename: the JSON file containing responses to speech transcription failure.
        :param spy_name: the name of the spy who the player communicates with.
        :param server_fail_responses_filename: the JSON file containing responses to the game not being able to perform
                                               the parsed action.
        """
        self.audio_filename = audio_filename
        self.transcribe = partial(transcribe, transcribe_fail_responses_filename)
        self.parse_action = partial(parse_action, self._get_chatbot(spy_name))
        self.send_to_server = partial(send_to_server, server_fail_responses_filename, server_addr)

    def run(self):
        """
        Records audio, then transcribes it, then parses the transcript into an action which is sent to the server.
        """
        result = record(self.audio_filename) \
                .then(self.transcribe) \
                .then(self.parse_action) \
                .then(self.send_to_server)

        if type(result) is SpeechSuccess:
            response_speech = result.value
        elif type(result) is SpeechFailure:
            response_speech = result.speech_err_message
        else:
            raise RuntimeError('unrecognised SpeechResult')

        say(response_speech)

    def run_loop(self):
        """
        Records audio, transcribes it, then parses the transcript into an action which is send to the server. This is
        done performed forever.
        """
        while True:
            input('Press Enter to start recording...')
            self.run()
