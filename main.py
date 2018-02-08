from speech.record import Recorder
from speech.transcribe import transcribe_file
from parsing.parse_action import action
from parsing.pre_processing import pre_process
from encoders.encode_action import ActionEncoder
from speech.voice import say
from actions.action import Action
import requests
import json


if __name__ == '__main__':
    server = "http://192.168.0.30:8080/action"

    while True:
        input('Press Enter to start/stop recording')

        recorder = Recorder(sample_rate=16000)
        recorder.record()
        recorder.write('output.wav')

        transcript = transcribe_file('output.wav')
        print('Transcribed:', transcript)

        if transcript:
            tokens = pre_process(transcript)
            result = action().parse(tokens)

            if result:
                print('Parsed             :', result.parsed)
                print('Certainty          :', result.response)
                print('Positive Responses :', result.parsed.responses())

                response = requests.post(server, json=json.loads(json.dumps(result.parsed, cls=ActionEncoder)))
                print('From server:', response)

                if response.status_code == 200:
                    say(result.parsed.random_response())
                else:
                    say(Action.random_negative_response())

            else:
                print('Failed to parse')

        print('\n')
