

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
        ['Done initialising', 600]
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

    promptStartRecord();
}

var is_key_down = false;

/**
 * Prompts the user to record by displaying a message.
 */
function promptStartRecord() {
    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML = `Press any to start recording...<br/>`;
    is_key_down = false;
}

/**
 * Prompts the user to stop recording by displaying a message.
 */
function promptStopRecord() {
    // Don't display the message multiple times if the user holding down a key.
    if (is_key_down) {
        return;
    }

    var recordDiv = document.querySelector('#record');
    recordDiv.innerHTML += `Release to stop recording...`;
    is_key_down = true;
}

/**
 * Adds event listeners for key up and key down to know when to stop and start recording.
 */
function setup() {
    document.addEventListener('keydown', promptStopRecord);
    document.addEventListener('keyup', promptStartRecord);
}

function start() {
    animateStartupText(displayTitle);
}

window.addEventListener('load', function() { setup(); start(); });
