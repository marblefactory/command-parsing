from app import app, socketio, GAME_MODE, FILL_CACHE, make_speech_responder, preload

if not GAME_MODE:
    print("WARNING: Not in Game Mode")

speech_responder = make_speech_responder()

# Filling the cache takes a long time as all the tests have to run.
preload(fill_cache=FILL_CACHE)

print('Running Server')
socketio.run(app, host='0.0.0.0', port=5000)
