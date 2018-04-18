"use strict";

// Used to recognise speech from the user, i.e. speech to text.
// This is initialised once the document is loaded.
var gRecognition = null;

// Used to communicate recognised speech back to the server,
// and for the server to reply with response speech to say.
// This is initialised once the document is loaded.
var gSocket = null;

// Whether to play the intro animation or not.
// This can be useful when debugging.
var gShouldPlayIntro = false;

/**
 * Plays the sound in the audio element with the given id.
 */
function play(id, volume = 1.0) {
    var audioElement = document.querySelector(id);
    audioElement.volume = volume;
    audioElement.play();
}

/**
 * Speaks the given text in the preferred voice. If the voice does not exist, the text is spoken in the first
 * available voice. Also, cancels any speech currently being spoken.
 */
function speak(text, preferred_voice, callback) {
    var msg = new SpeechSynthesisUtterance();
	msg.text = text;
	msg.rate = 1.07;
	msg.volume = 0.56;

    // If a voice has been selected, find the voice and set the
    // utterance instance's voice attribute.
	if (preferred_voice) {
		msg.voice = speechSynthesis.getVoices().filter((voice) => voice.name == preferred_voice)[0]
		         || speechSynthesis.getVoices()[0];
	}

    window.speechSynthesis.cancel();
	window.speechSynthesis.speak(msg);
	msg.onend = callback;
}

/**
 * Represents a state that the website can be in.
 */
class State {
    /**
     * @param {Element} stateDiv - the div in which text will be displayed.
     * @param {string} stateName - the name of the state. Used for logging.
     */
    constructor(stateDiv, stateName) {
        this.stateDiv = stateDiv;
        this.eventHandlers = [];
        this.stateName = stateName;
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
        console.log(`Entered: ${this.stateName}`);
    }

    /**
     * Called when the state is exited.
     * Can be used to perform cleanup such as removing event handlers.
     */
    exitState() {
        console.log(`Exited: ${this.stateName}`);

        for (var i=0; i<this.eventHandlers.length; i++) {
            var handlerRef = this.eventHandlers[i];
            document.removeEventListener(handlerRef.event, handlerRef.callback);
        }
    }

    /**
     * Leaves this state and enters the state constructed using newStateClass.
     * @param {Class} newStateClass - the class of the state to segue to.
     */
    segue(newStateClass) {
        var newState = new newStateClass(this.stateDiv);
        this.segueToState(newState);
    }

    /**
     * Leaves this state and enters the new state.
     * @param {State} newState - the new state to enter.
     */
    segueToState(newState) {
        this.exitState();
        newState.enterState();
    }
}

/**
 * The state before the connecting animation has started. Displays the text 'press any to connect'.
 */
class ConnectWaitingState extends State {
    constructor(stateDiv) {
        super(stateDiv, 'Connect Intro Waiting');
    }

    enterState() {
        super.enterState();

        this.stateDiv.innerHTML = 'Press any key to start connecting';
        super.addListener('keyup', () => super.segue(ConnectingState));
    }
}

/**
 * Displays a connecting animation, which is segued from once it is complete.
 */
class ConnectingState extends State {
    constructor(stateDiv) {
        super(stateDiv, 'Connecting Intro');
    }

    enterState() {
        super.enterState();

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
        play('#fax_machine', 0.3);
        this.stateDiv.innerHTML = '';
        addTexts(this.stateDiv, 0, () => super.segue(RecordWaitingState));
    }
}

/**
 * Displays a message to press a key to begin recording.
 */
class RecordWaitingState extends State {
    constructor(stateDiv) {
        super(stateDiv, 'Record Waiting');
    }

    enterState() {
        super.enterState();

        this.stateDiv.innerHTML = 'Press any to start recording...<br/>';
        super.addListener('keydown', () => super.segue(RecordingState));
    }

    exitState() {
        super.exitState();
        play('#radio_start', 0.6);
    }
}

/**
 * Displays a message to: release the key to stop recording.
 * Starts recognising the speech the user is saying when the state is entered.
 * Stopping recognising is done by the next state.
 */
class RecordingState extends State {
    constructor(stateDiv) {
        super(stateDiv, 'Recording');
    }

    enterState() {
        super.enterState();

        this.stateDiv.innerHTML += 'Release to stop recording...<br/>';

        gRecognition.onresult = this._onRecognitionResult.bind(this);
        gRecognition.onend = this._onNoRecognitionResult.bind(this);
        gRecognition.onnomatch = this._onNoRecognitionResult.bind(this);
        gRecognition.onerror = this._onRecognitionError.bind(this);

        // Stop is called by the next state.
        gRecognition.start();

        super.addListener('keyup', () => this._stopRecognition());
    }

    exitState() {
        super.exitState();
        play('#radio_static_end');

        gRecognition.onresult = null;
        gRecognition.onend = null;
        gRecognition.onnomatch = null;
        gRecognition.onerror = null;
    }

    /**
     * Stops the recogniser
     */
    _stopRecognition() {
        gRecognition.stop();
        this.stateDiv.innerHTML += '<br/>Sending...<br/>';
    }

    /**
     * Callback for the recogniser parsing speech.
     */
    _onRecognitionResult(event) {
        this._recognisedSpeech = true;

        var transcript = event.results[0][0].transcript;

        // Enter is not recognised for some reason.
        if (transcript == '\n') {
            transcript = 'enter'
        }

        console.log(`Recognised: ${transcript}`);

        var newState = new SendRecvSpeechState(transcript, this.stateDiv);
        super.segueToState(newState);
    }

    /**
     * Callback for the recogniser finishing parsing.
     * This is used to tell if the recogniser failed or not, since onnomatch does not work.
     */
    _onNoRecognitionResult(event) {
        if (!this._recognisedSpeech) {
            console.log("Failed to recognise speech");

            var newState = new SendRecvSpeechState(null, this.stateDiv);
            super.segueToState(newState);
        }
    }

    /**
     * Callback for an error occurring in parsing.
     */
    _onRecognitionError(event) {
        console.log(`Speech recognition error occurred: ${event.error}`);

        var newState = new SendRecvSpeechState(null, this.stateDiv);
        super.segueToState(newState);
    }
}

/**
 * Sends the recognised speech to the server,
 * and waits for the server to reply with the speech to say in response.
 * Once this is done it moves back to the RecordWaitingState for the
 * player to record a new message.
 */
class SendRecvSpeechState extends State {
    /**
     * @param {Optional[string]} recognisedSpeech - the recognised speech, or null if nothing was recognised.
     */
    constructor(recognisedSpeech, stateDiv) {
        super(stateDiv, 'SendRecvSpeech');
        this.recognisedSpeech = recognisedSpeech;
        this._listener = this._onSpeechResponseReceived.bind(this);
    }

    enterState() {
        super.enterState();

        gSocket.on('speech', this._listener);

        // Start sending the recognised speech to the server.
        if (this.recognisedSpeech) {
            gSocket.emit('recognised', this.recognisedSpeech);
        }
        else {
            gSocket.emit('not_recognised', {});
        }
    }

    exitState() {
        super.exitState();
        gSocket.removeEventListener('speech', this._listener);
    }

    /**
     * Callback for when the server responds with the speech to say.
     */
    _onSpeechResponseReceived(speech) {
        this.stateDiv.innerHTML += 'Received';
        // Speak the message, and play a 'radio end' tine after.
        speak(speech, 'Tom', speakEndCallback);

        function speakEndCallback() {
            // Add a small delay so it sounds more realistic.
            setTimeout(play('#radio_recv_end', 0.3), 20)
        }

        // Short delay so the 'received' message appears while the spy is talking.
        setTimeout(() => super.segue(RecordWaitingState), 1500);
    }
}

/**
 * Connects a socket to the server. This is used to receive the text to say in response to the user's command.
 * The callback is called once the socket is connected.
 */
function setupSocket(callback) {
    gSocket = io.connect('http://' + document.domain + ':' + location.port);

    // Emit a connected message to let the server that we are connected.
    gSocket.on('connect', function() {
        console.log("Connected to server");
        callback();
    });
}

function start() {
    addEventListener("click", function() {
        var el = document.documentElement;
        var rfs = el.requestFullScreen
               || el.webkitRequestFullScreen
               || el.mozRequestFullScreen;
        rfs.call(el);
    });

    // Setup global variables.
    gRecognition = new webkitSpeechRecognition();

    var stateDiv = document.querySelector('#state');

    var initialStateConstructor = gShouldPlayIntro ? ConnectWaitingState : RecordWaitingState;
    var initialState = new initialStateConstructor(stateDiv);

    // Initialise the socket.
    setupSocket(function() {
        // Prompt loading the voices.
        speechSynthesis.getVoices();

        window.speechSynthesis.onvoiceschanged = function() {
            initialState.enterState();
        }
    });
}

window.addEventListener('load', start);
