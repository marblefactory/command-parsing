# command-parsing

Performing speech to text, then parsing an action from the text.



## To Run


Create the environment:
```
$ python3.6 -m venv venv
$ source venv/bin/activate
```

Enter envitonment and install depends:
```
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
```

Download the NLTK lib bits:
```
(venv) $ python -m nltk.downloader wordnet
(venv) $ python -m nltk.downloader averaged_perceptron_tagger
```

Export the application name
```
(venv) $ export FLASK_APP=speech_server.py
```


Run the server
```
(venv) $ flask run
```

Note: If you want debug mode:
```
(venv) $ export FLASK_DEBUG=1
(venv) $ flask run
```
