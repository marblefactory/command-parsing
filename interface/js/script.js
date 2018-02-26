
/**
 * Sends a GET requst to the server, with the given url_postfix added to the
 * end of the url of the server.
 */
function get(url_postfix, callback) {
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200 && callback != undefined) {
            callback(request.responseText);
        }
    }

    url = window.location.origin + '/' + url_postfix;
    request.open("GET", url, true);
    request.send(null);
}

/**
 * Animates displaying a list of sentences to display on newlines one after the other.
 */
function animateStartupText(callback) {
    // The text to display and the time (ms) to wait before showing the next text.
    var texts = [
        ['SpySpeakBIOS 4.0 Release 6.0', 500],
        ['Copyright 2005-2018 SpySpeak Technologies Ltd.', 100],
        ['', 500],
        ['BIOS version 29.02', 100],
        ['Gateway Solo 9550', 120],
        ['System Id = 513', 110],
        ['Build Time; 09/10/2017', 200],
        ['', 600],
        ['639 KB System RAM Passed', 70],
        ['254 KB Extended RAM Passed', 100],
        ['512 K Cache Passed', 90],
        ['System BIOS Shadowed', 0],
        ['', 50],
        ['Done initialising', 1000]
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
var state = 0;

let START_STATE = 0;
let STOP_STATE = 1;
let ENCRYPT_STATE = 2;
let SENT_STATE = 3;

/**
 * Prompts the user to record by displaying a message.
 */
function promptStartRecord() {
    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML = `Press any to start recording...<br/>`;
    state = START_STATE;
}

/**
 * Prompts the user to stop recording by displaying a message.
 */
function promptStopRecord(recogniser) {
    // Don't display the message multiple times if the user holding down a key.
    if (state != START_STATE) {
        return;
    }

    console.log(recogniser);

    recogniser.start();
    state = STOP_STATE;

    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML += `Release to stop recording...<br/><br/>`;
}

/**
 * Displays an 'encrypting' message to mask any delay from parsing the speech by the server.
 */
function displayEncryptingMessage(recogniser) {
    if (state != STOP_STATE) {
        return;
    }

    recogniser.stop();
    state = ENCRYPT_STATE;

    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML += `Encrypting: `;

    // Adds num '#' to the end of the loading bar, with a randomised delay between adding them.
    function extendLoadingBar(num) {
        // If there is nothing left to add to the loading bar, or we are no longer in the encrypting state.
        if (num == 0 || state != ENCRYPT_STATE) {
            return;
        }

        recordDiv.innerHTML += '#';

        var waitTime = Math.random() * (200 - 50) + 50;
        setTimeout(() => extendLoadingBar(num - 1), waitTime);
    }

    extendLoadingBar(50);
}

/**
 * Displays a 'sent' message and prompts the user to record a message again.
 */
function displaySentAndRestart() {
    if (state != ENCRYPT_STATE) {
        return;
    }

    state = SENT_STATE;

    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML += `<br/><br/>Sent`;

    setTimeout(promptStartRecord, 650);
}

/**
 * Called when the speech recognition has recognised the text.
 */
function didRecogniseSpeech(event) {
    if (state != ENCRYPT_STATE) {
        throw 'unexpected state';
    }

    console.log(event.results[0][0].transcript);
}


/**
 * Adds event listeners for key up and key down to know when to stop and start recording.
 */
function start() {
    // Used to recognise audio.
    var recogniser = new webkitSpeechRecognition();
    recogniser.continuous = true;
    recogniser.onresult = didRecogniseSpeech;

    document.addEventListener('keydown', () => promptStopRecord(recogniser));
    document.addEventListener('keyup', () => displayEncryptingMessage(recogniser));

    animateStartupText(didFinishAnimation);

    function didFinishAnimation() {
        displayTitle();
        promptStartRecord();
    }
}

window.addEventListener('load', start);
