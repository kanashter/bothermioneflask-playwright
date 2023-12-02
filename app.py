from flask import Flask
from flask import request, jsonify
import urllib.request
from functions import collect_data
import urllib.parse

app = Flask(__name__)

def get(username, password):
    data = collect_data(username, password)
    return jsonify(data)

@app.route('/', methods=['GET'])
def run():
    try:
        username = urllib.parse.unquote_plus(request.args['username'])
        password = urllib.parse.unquote_plus(request.args['password'])
    except:
        resp = {
            'error': 'No Username/Password provided'
        }
        data = jsonify(resp)
        data.headers.add('Access-Control-Allow-Origin', '*')
        return data
    try:
        data = get(username, password)
        data.headers.add('Access-Control-Allow-Origin', '*')
        return data
    except Exception as e:
        resp = {
            'error': "Incorrect Login"
        }
        data = jsonify(resp)
        data.headers.add('Access-Control-Allow-Origin', '*')
        return data


if __name__ == "__main__":
    app.run()
