from app import app, socketio, GAME_MODE, FILL_CACHE, preload


print('GAME MODE:', GAME_MODE)
print('FILL_CACHE:', FILL_CACHE)

# Filling the cache takes a long time as all the tests have to run.
preload(fill_cache=FILL_CACHE)
print("Done Cache")


if __name__ == '__main__':
    print('Running Server')
    socketio.run(app, host='0.0.0.0', port=5000)


# sudo gunicorn --certfile=cert.pem --keyfile=key.pem --worker-class=eventlet -w 1 -b localhost:443 speech_server:app