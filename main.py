import argparse
import json
import threading
import re
from collections import namedtuple
from uuid import uuid4

from flask import Flask, render_template, request, jsonify
from waitress import serve
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import MethodNotAllowed, NotFound

RESPONSES = {}
REQUESTS = []
REQUESTS_LOCK = threading.RLock()
CapturedRequest = namedtuple('CapturedRequest', ['id', 'path', 'args', 'method', 'headers', 'body'])
app = Flask(__name__)
app.debug = True


def args_match(resp: dict, cr: CapturedRequest) -> bool:
    return all([resp['args'][key] == cr.args[key][0] or resp['args'][key] == '*' for key in cr.args.keys()])


def methods_match(resp: dict, cr: CapturedRequest) -> bool:
    return not resp.get('methods') or cr.method.lower() in resp['methods'] or resp['methods'] == '*'


@app.route('/')
def index():
    global REQUESTS

    return render_template('index.html', requests=REQUESTS)


@app.route('/<path:path>', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
def catch_all(path):
    global REQUESTS
    global REQUESTS_LOCK

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
    potential_responses = None

    pr = RESPONSES.get(cr.path)
    for pattern, responses in RESPONSES.items():
        match = re.match(pattern, cr.path)
        if match:
            if potential_responses:
                raise IndexError('Multiple path patterns match, please reconfigure responses.')

            potential_responses = responses
            # Any named groups in path will be extracted here
            path_params = match.groupdict()

    if potential_responses is None:
        raise NotFound

    for resp in potential_responses:
        if args_match(resp, cr) and methods_match(resp, cr):
            data = resp['response']

            if isinstance(data, dict):
                # extra brackets are to prevent format from interpreting keys as references
                data = '{' + json.dumps(data) + '}'

            if path_params:
               data = data.format(**path_params)

            if isinstance(data, str):
                data = re.sub('^{{', '{', data)
                data = re.sub('}}$', '}', data)

            return data, resp.get('status_code', 200)

    # TODO: MethodNotAllowed is raised both if methods didn't match and if no args didn't match, but ideally the second
    # should raise a different HTTP error.
    raise MethodNotAllowed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sham')
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
