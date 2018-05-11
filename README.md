# Spy Speak Command Parsing

- Runs a server to host a web app allowing the player in input audio.
- Speech to Text is performed using the Js webkitSpeechRecognition API.
- Text to Action parsing is performed by the backend.


## To Run


Create the environment:

```
$ python3.6 -m venv venv
$ source venv/bin/activate
```

Enter environment and install depends:

```
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
```

Download the NLTK lib bits:

```
(venv) $ python -m nltk.downloader wordnet
(venv) $ python -m nltk.downloader averaged_perceptron_tagger
```

Run the server, using gunicorn for HTTPS. This allows the microphone to be
used with Chrome when another device is running the server.

```
(venv) $ sudo gunicorn --certfile=cert.pem --keyfile=key.pem --worker-class=eventlet -w 1 -b 0.0.0.0:443 -t 36000 speech_server:app
```
