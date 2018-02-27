"use strict";

// Used to disable/enable animations at startup.
var skipIntro = true;

/**
 * Sends a post request to the server, with the given ulr_postfix added to the
 * end of the url of the server.
 */
function post(url_postfix, obj, callback) {
    var request = new XMLHttpRequest();
    var url = window.location.origin + '/' + url_postfix;

    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200 && callback != undefined) {
            callback(request.responseText);
        }
    }

    request.open("POST", url, true);
    request.setRequestHeader('Content-Type', 'application/json');
    request.send(JSON.stringify(obj));
}

/**
 * Returns a random number between min and max.
 */
function random(maxMs, minMs) {
    return Math.random() * (maxMs - minMs) + minMs;
}

/**
 * Plays the sound in the audio element with the given id.
 */
function play(id) {
    var audioElement = document.querySelector(id);
    audioElement.play();
}

/**
 * Speaks the given text in the preferred voice. If the voice does not exist, the text is spoken in the first
 * available voice.
 */
function speak(text, preferred_voice) {
    var msg = new SpeechSynthesisUtterance();
	msg.text = text;
	msg.rate = 218; // words per min.

    // If a voice has been selected, find the voice and set the
    // utterance instance's voice attribute.
	if (preferred_voice) {
		msg.voice = speechSynthesis.getVoices().filter((voice) => voice.name == preferred_voice)[0]
		         || speechSynthesis.getVoices()[0];
	}

	window.speechSynthesis.speak(msg);
}

/**
 * Animates displaying a list of sentences to display on newlines one after the other.
 */
function animateStartupText(callback) {
    // The text to display and the time (ms) to wait before showing the next text.
    var texts = [
        ['', 100],
        ['SpySpeakBIOS 4.0 Release 6.0', 450],
        ['Copyright 2005-2018 SpySpeak Technologies Ltd.', 100],
        ['', 450],
        ['BIOS version 29.02', 100],
        ['Gateway Solo 9550', 120],
        ['System Id = 513', 110],
        ['Build Time; 09/10/2017', 200],
        ['', 550],
        ['639 KB System RAM Passed', 70],
        ['254 KB Extended RAM Passed', 100],
        ['512 K Cache Passed', 90],
        ['System BIOS Shadowed', 0],
        ['', 50],
        ['Connecting to host...', 850],
        ['Done connecting', 500]
    ];

    var body = document.querySelector('#boot_jargon');

    function addTexts(index) {
        if (index === texts.length) {
            callback();
            return;
        }

        var text = `${texts[index][0]}<br/>`;
        var waitTime = texts[index][1];

        body.innerHTML += text;

        setTimeout(() => addTexts(index + 1), waitTime);
    }

    // Start the animation.
    play('#fax_machine');
    addTexts(0);
}

/**
 * Hides the loading Jargon and displays the SpySpeak title.
 */
function displayTitle() {
    var bootJargonDiv = document.querySelector('#boot_jargon');
    var bootedDiv = document.querySelector('#booted');

    bootJargonDiv.style.display = 'none';
    bootedDiv.style.display = 'block';
}

// Used to ensure we enter states record, stop, encrypt, in the correct order.
let WAITING_STATE = 0;
let LISTENING_STATE = 1;
let SENDING_STATE = 2;
let RECEIVED_STATE = 3;

var state = -1;

// Needed because onnomatch does not work.
var didRecognise = false;

/**
 * Prompts the user to record by displaying a message.
 */
function promptStartRecord() {
    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML = `Press any to start recording...<br/>`;

    // Update state
    state = WAITING_STATE;
    didRecognise = false;
}

/**
 * Prompts the user to stop recording by displaying a message.
 */
function promptStopRecord(recogniser) {
    // Don't display the message multiple times if the user holding down a key.
    if (state != WAITING_STATE) {
        return;
    }

    state = LISTENING_STATE;
    recogniser.start();

    // Play a sound when the user presses down a key.
    play('#radio_start');

    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML += `Release to stop recording...<br/><br/>`;
}

/**
 * Displays a sending message to mask any delay.
 */
function displaySendingMessage(recogniser) {
    if (state != LISTENING_STATE) {
        return;
    }

    state = SENDING_STATE;
    recogniser.stop();

    // Play a sound when the user released a key.
    play('#radio_end');

    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML += `Sending...<br/>`;
}

/**
 * Called when the speech recognition has recognised the text. Sends the recognised text to the server then displays
 * a 'sent' message.
 */
function didRecogniseSpeech(event, socket) {
    if (state != SENDING_STATE) {
        throw 'unexpected state at success';
    }

    // This is called before `checkDidFailToRecognise`.
    didRecognise = true;

    // Send the transcript to the server.
    var transcript = event.results[0][0].transcript;
    console.log(`Sending recognised: ${transcript}`);
    socket.emit('recognised', transcript);
}

/**
 * Called if the speech recognition did not recognise any speech. Sends a message to the server that nothing was
 * recognised. Then displays a 'sent' message.
 */
function checkDidFailToRecognise(event, socket) {
    if (state !== SENDING_STATE) {
        throw 'unexpected state at finish';
    }

    if (!didRecognise) {
        console.log('Sending recognised: nothing');
        socket.emit('not_recognised', {});
    }
}

/**
 * Displays a message saying the message was received.
 */
function displayReceivedMessage() {
    if (state != SENDING_STATE) {
        throw 'unexpected state at received';
    }

    state = RECEIVED_STATE;

    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML += `Received`;
}

/**
 * Called when response speech has been received from the server. This speaks the speech then restarts the loop.
 */
function didReceiveResponseSpeech(speech) {
    if (state != SENDING_STATE) {
        throw 'unexpected state at receive response speech';
    }

    displayReceivedMessage();

    // A short delay to display the 'received' message while no speech is said.
    // This makes it appear as if the spy is thinking.
    setTimeout(speakThenRestart, 300);

    function speakThenRestart() {
        speak(speech, 'Tom');
        promptStartRecord();
    }
}

/**
 * Adds event listeners for key up and key down to know when to stop and start recording.
 */
function start(socket) {
    // Used to recognise audio.
    var recogniser = new webkitSpeechRecognition();
    recogniser.continuous = true;
    recogniser.onresult = (event) => didRecogniseSpeech(event, socket);
    recogniser.onend = (event) => checkDidFailToRecognise(event, socket);

    document.addEventListener('keydown', () => promptStopRecord(recogniser));
    document.addEventListener('keyup', () => displaySendingMessage(recogniser));

    function didFinishAnimation() {
        displayTitle();
        promptStartRecord();
    }

    if (skipIntro) {
        didFinishAnimation();
    } else {
        animateStartupText(didFinishAnimation);
    }
}

/**
 * Connects a socket to the server. This is used to receive the text to say in response to the user's command.
 * The callback is called once the socket is connected.
 */
function setupSocket(callback) {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    // Emit a connected message to let the server that we are connected.
    socket.on('connect', function() {
        console.log("Connected to server");
        callback(socket);
    });

    socket.on('speech', didReceiveResponseSpeech);
}

/**
 * Loads the voices for text to speech, then calls start once it is done.
 * This is because loading may be done asynchronously.
 */
function loadVoices() {
    setupSocket(function(socket) {
        // Prompt loading the voices.
        speechSynthesis.getVoices();

        window.speechSynthesis.onvoiceschanged = function() {
            start(socket);
        }
    });
}

window.addEventListener('load', loadVoices);
