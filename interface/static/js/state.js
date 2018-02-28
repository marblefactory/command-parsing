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
     * @param {boolean} shouldClearStateDiv - whether to remove any html inside the div on exiting the state.
     */
    constructor(stateDiv, shouldClearStateDiv) {
        this.stateDiv = stateDiv;
        this.shouldClearStateDiv = shouldClearStateDiv;
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
        console.log("HERE");
        console.log(this.shouldClearStateDiv);
        if (this.shouldClearStateDiv) {
            console.log("CLEARED");
            this.stateDiv.innerHTML = '';
        }

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
        super(stateDiv, true);
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
        super(stateDiv, true);
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
        addTexts(this.stateDiv, 0, () => console.log("DONE"));
    }
}

function start() {
    var stateDiv = document.querySelector('#state');

    var x = new ConnectWaitingState(stateDiv);
    x.enterState();
}

window.addEventListener('load', start);