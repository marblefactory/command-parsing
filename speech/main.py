from speech.record import Recorder
from speech.transcribe import transcribe_file
from parsing.parse_action import action


if __name__ == '__main__':
    while True:
        input('Press Enter to start/stop recording')

        recorder = Recorder(sample_rate=16000)
        recorder.record()
        recorder.write('output.wav')

        text = transcribe_file('output.wav')
        print('Transcribed:', text)

        result = action().parse(text.split(' '))

        if result:
            print('Parsed   :', result.parsed)
            print('Certanity:', result.response)
        else:
            print('Failed to parse')
