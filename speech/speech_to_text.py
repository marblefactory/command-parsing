import speech_recognition as sr
import json
from parsing.parse_action import action
from parsing.parse_action import ParseResult
from encoders.encode_action import ActionEncoder

import requests

server = "http://192.168.0.101:8080/action"


# if __name__ == '__main__':
#     instructions = [
#         'stop',
#         'go crouched to lab 300',
#         'stand up',
#         'pick up the rock on your right',
#         'run to the gun range',
#         'throw the rock',
#         'go backwards',
#         'go to the first door on your left',
#         'run to server room 301',
#         'go to the door on your right',
#     ]
#
#     while (True):
#         for j, instruction in enumerate(instructions):
#             print('[',j,']',instruction)
#
#         i = int(input("\nindex:"))
#
#
#         print('Parsing')
#         result = action().parse(instructions[i].split())
#
#         if result:
#             print('Parsed')
#
#             action_json = json.loads(json.dumps(result.parsed, cls=ActionEncoder))
#
#             print('Sending :', action_json)
#             server_response = requests.post(server, json=action_json)
#             print(server_response)
#
#         else:
#             print('No parse')
#
#         print('\n')


# this is called from the background thread
def callback(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    print('Parsing')
    try:
        print("Google Speech Recognition thinks you said " + recognizer.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def choose_mic():
    print("Choose a microphone:")

    mic_names = sr.Microphone.list_microphone_names()

    for i, mic_name in enumerate(mic_names):
        print('\t[', i + 1, '] ', mic_name)

    chosen_index = -1
    while not (0 <= chosen_index < len(mic_names)):
        chosen_index = int(input('Index: ')) - 1

    print('Chose:', mic_names[chosen_index])

    return sr.Microphone(device_index=chosen_index)


def print_parsed(parse_result: ParseResult):
    if not parse_result:
        print('FAILURE: No parse')
        return

    parsed, response, _ = parse_result

    print('PARSED:', parsed)
    print('RESPONSE:',response,'\n')


if __name__ == '__main__':
    rec = sr.Recognizer()
    mic = choose_mic()

    with mic as source:
        print('Adjusting for ambient noise')
        rec.adjust_for_ambient_noise(mic, duration = 2)
        print('Done adjusting')

    GOOGLE_CLOUD_SPEECH_CREDENTIALS = json.dumps(json.load(open('../google_cloud_speech_credentials.json')))

    while True:
        print("Say something:")

        with mic as source:
            audio = rec.listen(source)

        try:
            print('Recognising')
            text = rec.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
            words = text.lower().split()

            print('Understanding')
            result = action().parse(words)

            print('Got:', text)
            print_parsed(result)

            if result:
                print("Sending :", json.dumps(result.parsed, cls=ActionEncoder))
                server = "http://192.168.0.101:8080/action"
                requests.post(server, json=json.loads(json.dumps(result.parsed, cls=ActionEncoder)))

        except sr.UnknownValueError:
            print("Oops! Didn't catch that")
        except sr.RequestError as e:
            print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))

        # while True:
        #     input()
        #     print('Listening')
        #     stop_listening = rec.listen_in_background(source, callback)
        #     input()
        #     print('Stopped')
        #     stop_listening()
