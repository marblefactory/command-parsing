from flask import Flask, render_template, send_from_directory, jsonify, request

app = Flask(__name__, static_url_path='')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognised', methods=['POST'])
def recognised_speech():
    transcript = request.get_json(silent=True)
    print('Recognised', transcript)

    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)
