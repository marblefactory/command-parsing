from speech.record import Recorder
from speech.transcribe import transcribe_file
from parsing.parse_action import action
from parsing.pre_processing import pre_process


if __name__ == '__main__':
    while True:
        input('Press Enter to start/stop recording')

        recorder = Recorder(sample_rate=16000)
        recorder.record()
        recorder.write('output.wav')

        transcript = transcribe_file('output.wav')
        print('Transcribed:', transcript)

        if (transcript):
            tokens = pre_process(transcript)
            result = action().parse(tokens)

            if result:
                print('Parsed   :', result.parsed)
                print('Certanity:', result.response)
            else:
                print('Failed to parse')

        print('\n')
