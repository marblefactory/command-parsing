from app import app, socketio, GAME_MODE, FILL_CACHE, preload


if __name__ == '__main__':
    if not GAME_MODE:
        print("WARNING: Not in Game Mode")

    # Filling the cache takes a long time as all the tests have to run.
    preload(fill_cache=FILL_CACHE)

    print('Running Server')
    socketio.run(app, host='0.0.0.0', port=5000)
