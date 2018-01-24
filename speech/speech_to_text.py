import speech_recognition as sr
import json

r = sr.Recognizer()
m = sr.Microphone()


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
            if str is bytes:
                print(u"You said {}".format(text).encode("utf-8"))
            else:
                print("You said {}".format(text))
        except sr.UnknownValueError:
            print("Oops! Didn't catch that")
        except sr.RequestError as e:
            print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))

except KeyboardInterrupt:
    pass
