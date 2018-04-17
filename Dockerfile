# docker build -t ubuntu1604py36
FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y software-properties-common vim
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv
RUN apt-get install -y git

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel



RUN adduser --disabled-password speech_server

WORKDIR /home/speech_server

COPY requirements.txt requirements.txt
RUN python3.6 -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt

COPY app app
COPY actions actions
COPY encoders encoders
COPY failure_responses failure_responses
COPY interface interface
COPY parsing parsing
COPY tests tests

COPY speech_server.py equatable.py utils.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP speech_server.py

RUN chown -R speech_server:speech_server ./
USER speech_server

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
