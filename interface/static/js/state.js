"use strict";

/**
 * Represents a state that the website can be in.
 */
class State {
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
        console.log(`NUM = ${this.eventHandlers}`);
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
        this.stateDiv.innerHTML = 'Press any key to connect';
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
        this.stateDiv.innerHTML = "HERE";
    }
}

function start() {
    var stateDiv = document.querySelector('#state');

    var x = new ConnectWaitingState(stateDiv);
    x.enterState();
}

window.addEventListener('load', start);