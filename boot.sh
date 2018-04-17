#!/bin/sh
source venv/bin/activate
sleep 10
python -m nltk.downloader wordnet
exec gunicorn -b :5000 --access-logfile - --error-logfile - octolink:app
