import argparse
import json
import threading
from collections import namedtuple
from uuid import uuid4

from flask import Flask, render_template, request, jsonify
from waitress import serve
from werkzeug.datastructures import ImmutableMultiDict

RESPONSES = {}
REQUESTS = []
REQUESTS_LOCK = threading.RLock()
CapturedRequest = namedtuple('CapturedRequest', ['id', 'path', 'args', 'method', 'headers', 'body'])
app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    global REQUESTS

    return render_template('index.html', requests=REQUESTS)


@app.route('/<path:path>', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
# @app.route('/<path:path>')
def catch_all(path):
    global REQUESTS
    global REQUESTS_LOCK
    args = []

    if path == 'favicon.ico':
        return 'Not Found', 404

    if request.is_json:
        data = request.json
    else:
        data = request.data

    cr = CapturedRequest(str(uuid4()), path, dict(request.args), request.method, request.headers, data)

    with REQUESTS_LOCK:
        REQUESTS.append(cr)

        if len(REQUESTS) > 10:
            REQUESTS.pop(0)

    # Here we search the RESPONSES object to see if we have a response to return.
    # TODO: currently this only checks the path and query args, we should add another parameter "method" so we can
    # allow users to specify different responses based on their request method of choice.
    potential_responses = RESPONSES.get(cr.path)

    if potential_responses is not None:
        for resp in potential_responses:
            if resp['args'] == cr.args:
                data = resp['response']

                if isinstance(data, dict):
                    return jsonify(**data)
                else:
                    return data

    return jsonify(success=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grice')
    parser.add_argument('port', help='The port to bind to')
    parser.add_argument('--responses', default=None, help='Path to responses file in JSON format.')
    args = parser.parse_args()

    if args.responses:
        with open(args.responses) as f:
            RESPONSES = json.load(f)

    for resp_list in RESPONSES.values():
        for resp in resp_list:
            resp['args'] = ImmutableMultiDict(resp.get('args', {}))

    serve(app, host='0.0.0.0', port=args.port, threads=4)
