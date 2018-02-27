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
let ENCRYPTING_STATE = 2;
let SENDING_STATE = 3;

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
 * Displays an 'encrypting' message to mask any delay from parsing the speech by the server.
 */
function displayEncryptingMessage(recogniser) {
    if (state != LISTENING_STATE) {
        return;
    }

    state = ENCRYPTING_STATE;
    recogniser.stop();

    // Play a sound when the user released a key.
    play('#radio_end');

    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML += `Encrypting...`;
}

/**
 * Called when the speech recognition has recognised the text. Sends the recognised text to the server.
 */
function didRecogniseSpeech(event) {
    if (state != ENCRYPTING_STATE) {
        throw 'unexpected state at success';
    }

    // This is called before `checkDidFailToRecognise`.
    didRecognise = true;

    // Send the transcript to the server.
    var transcript = event.results[0][0].transcript;
    console.log(`Recognised: ${transcript}`);
    post('recognised', transcript, displaySentAndRestart);
}

/**
 * Called if the speech recognition did not recognise any speech. Sends a message to the server that nothing was
 * recognised.
 */
function checkDidFailToRecognise() {
    if (state != ENCRYPTING_STATE) {
        throw 'unexpected state at finish';
    }

    if (!didRecognise) {
        // Wait a short time to make it appear like the spy is thinking.
        // Otherwise he replies too quickly.
        setTimeout(() => post('not_recognised', {}, displaySentAndRestart), random(600, 300));
    }
}

/**
 * Displays a 'sent' message and prompts the user to record a message again.
 */
function displaySentAndRestart() {
    if (state != ENCRYPTING_STATE) {
        return;
    }

    state = SENDING_STATE;

    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML += `<br/><br/>Sent`;

    setTimeout(promptStartRecord, 1500);
}

/**
 * Adds event listeners for key up and key down to know when to stop and start recording.
 */
function start() {
    // Used to recognise audio.
    var recogniser = new webkitSpeechRecognition();
    recogniser.continuous = true;
    recogniser.onresult = didRecogniseSpeech;
    recogniser.onend = checkDidFailToRecognise;

    document.addEventListener('keydown', () => promptStopRecord(recogniser));
    document.addEventListener('keyup', () => displayEncryptingMessage(recogniser));

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
 * Loads the voices for text to speech, then calls start once it is done.
 * This is because loading may be done asynchronously.
 */
function loadVoices() {
    // Prompt loading the voices.
    speechSynthesis.getVoices();

    //var socket = io('http://localhost');

    window.speechSynthesis.onvoiceschanged = function() {
        start();
    }
}

window.addEventListener('load', loadVoices);
