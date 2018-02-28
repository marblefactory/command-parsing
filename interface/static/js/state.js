"use strict";

/**
 * Plays the sound in the audio element with the given id.
 */
function play(id) {
    var audioElement = document.querySelector(id);
    audioElement.play();
}

/**
 * Represents a state that the website can be in.
 */
class State {
    /**
     * @param {Element} stateDiv - the div in which text will be displayed.
     */
    constructor(stateDiv) {
        this.stateDiv = stateDiv;
        this.eventHandlers = [];
    }

    /**
     * Adds an event handler on the given event to fire the callback.
     * The event handler will be automatically removed when the state is exited.
     */
    addListener(event, callback) {
        document.addEventListener(event, callback);

        // Used to remove the event handler.
        var handlerRef = {
            event: event,
            callback: callback
        };

        this.eventHandlers.push(handlerRef);
    }

    /**
     * Called when the state is entered.
     * Can be used to display any text required in the state div, and add event handlers.
     */
    enterState() {
    }

    /**
     * Called when the state is exited.
     * Can be used to perform cleanup such as removing event handlers.
     */
    exitState() {
        for (var i=0; i<this.eventHandlers.length; i++) {
            var handlerRef = this.eventHandlers[i];
            document.removeEventListener(handlerRef.event, handlerRef.callback);
        }
    }

    /**
     * Leaves this state and enters the new state.
     * @param {Class} newStateClass - the class of the state to segue to.
     */
    segue(newStateClass) {
        var newState = new newStateClass(this.stateDiv);
        this.exitState();
        newState.enterState();
    }
}

/**
 * The state before the connecting animation has started. Displays the text 'press any to connect'.
 */
class ConnectWaitingState extends State {
    constructor(stateDiv) {
        super(stateDiv);
    }

    enterState() {
        this.stateDiv.innerHTML = 'Press any key to start connecting';
        super.addListener('keyup', () => super.segue(ConnectingState));
    }
}

/**
 * Displays a connecting animation, which is segued from once it is complete.
 */
class ConnectingState extends State {
    constructor(stateDiv) {
        super(stateDiv);
    }

    enterState() {
        // The text to display and the time (ms) to wait before showing the next text.
        var texts = [
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

        function addTexts(stateDiv, index, callback) {
            if (index === texts.length) {
                callback();
                return;
            }

            var text = `${texts[index][0]}<br/>`;
            var waitTime = texts[index][1];
            stateDiv.innerHTML += text;

            setTimeout(() => addTexts(stateDiv, index + 1, callback), waitTime);
        }

        // Start the animation.
        play('#fax_machine');
        this.stateDiv.innerHTML = '';
        addTexts(this.stateDiv, 0, () => super.segue(RecordWaitingState));
    }
}

/**
 * Displays a message to: press a key to begin recording.
 */
class RecordWaitingState extends State {
    constructor(stateDiv) {
        super(stateDiv);
    }

    enterState() {
        this.stateDiv.innerHTML = 'Press any to start recording...<br/>';
        super.addListener('keydown', () => super.segue(RecordingState));
    }

    exitState() {
        super.exitState();
        play('#radio_start');
    }
}

/**
 * Displays a message to: release the key to stop recording.
 */
class RecordingState extends State {
    constructor(stateDiv) {
        super(stateDiv);
    }

    enterState() {
        this.stateDiv.innerHTML += 'Release to stop recording...<br/>';
        super.addListener('keyup', () => super.segue(SendingState))
    }

    exitState() {
        super.exitState();
        play('#radio_end');
    }
}

/**
 * Displays a message that the recorded is being sent to the spy.
 * This is displayed while we're waiting for the speech to text to finish,
 * and then for the server to give a speech to respond with, i.e. to speak.
 */
class SendingState extends State {
    constructor(stateDiv) {
        super(stateDiv);
    }

    enterState() {
        this.stateDiv.innerHTML += '<br/>Sending...';

        // TEMPORARY
        setTimeout(() => super.segue(ReceivedState), 1000);
    }
}

/**
 * Displays a message that the recorded speech was received and plays the response of the spy.
 * After a short delay (while the spy is possibly still talking) it moves back to the RecordWaitingState for the
 * player to record a new message.
 */
class ReceivedState extends State {
    constructor(stateDiv) {
        super(stateDiv);
    }

    enterState() {
        this.stateDiv.innerHTML += '<br/>Received';
        setTimeout(() => super.segue(RecordWaitingState), 1500);
    }
}


function start() {
    var stateDiv = document.querySelector('#state');

    var x = new RecordWaitingState(stateDiv);//new ConnectWaitingState(stateDiv);
    x.enterState();
}

window.addEventListener('load', start);