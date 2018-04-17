#!/bin/bash
source venv/bin/activate
sleep 10
python -m nltk.downloader wordnet
python -m nltk.downloader averaged_perceptron_tagger

exec gunicorn -b :5000 -w 1 --access-logfile - --error-logfile - speech_server:app
