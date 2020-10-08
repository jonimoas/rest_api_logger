import os
import requests
from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
import urllib.parse
import json
import datetime
from tinydb import TinyDB, Query
db = TinyDB('db.json')
app = Flask(__name__)


@app.route('/<path:path>', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def main(path):
    method = request.method
    args = request.args.to_dict(flat=False)
    headers = dict(request.headers)
    body = request.get_json()
    response = requests.request(method, os.environ["API_TO_WATCH"]+path, params=args, stream=True,
                                headers=headers, allow_redirects=False, data=json.dumps(body))
    response_body = None
    response_headers = dict(response.headers)
    try:
        response_body = response.json()
    except:
        response_body = None
    db.insert(dict({'method': request.method,
                    'path': str(path),
                    'args': args,
                    'request_headers': headers,
                    'request_body': body,
                    'response': response_body,
                    'response_headers': response_headers,
                    'timestamp': str(datetime.datetime.now()),
                    'status': response.status_code
                    }))
    result = None
    if response_body != None:
        result = jsonify(response_body)
    else:
        result = Response()
    result.status_code = response.status_code
    result.headers = response_headers
    return result
