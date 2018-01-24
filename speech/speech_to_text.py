import speech_recognition as sr
import json
from parsing.parse_action import single_action
from parsing.parser import ParseResult


r = sr.Recognizer()
m = sr.Microphone()


def print_parsed(parse_result: ParseResult):
    if not parse_result:
        print('FAILURE: No parse')
        return

    parsed, response, _ = parse_result

    print('PARSED:', parsed)
    print('RESPONSE:',response,'\n')


if __name__ == '__main__':
    try:
        print("Geting ambinent noise")
        with m as source: r.adjust_for_ambient_noise(source)
        print("Energy threshold established")
        GOOGLE_CLOUD_SPEECH_CREDENTIALS = json.dumps(json.load(open('../google_cloud_speech_credentials.json')))

        while True:
            print("Say something:")
            with m as source: audio = r.listen(source)
            print("Will now convert to text...")
            try:
                text = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)

                result = single_action().parse(text.split())
                print('\n')
                print_parsed(result)

            except sr.UnknownValueError:
                print("Oops! Didn't catch that")
            except sr.RequestError as e:
                print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))

    except KeyboardInterrupt:
        pass
