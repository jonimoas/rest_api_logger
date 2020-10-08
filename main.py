from waitress import serve
import os
import requests
from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask import after_this_request
import urllib.parse
import json
import datetime
from tinydb import TinyDB, Query
currentDate = datetime.datetime.today()
dateString = str(currentDate.year)+"-" + \
    str(currentDate.month) + "-" + str(currentDate.day)
db = TinyDB("db"+dateString+".json")
app = Flask(__name__)


@app.route('/<path:path>', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def main(path):
    global currentDate
    global db
    if currentDate.day != datetime.datetime.now().day:
        currentDate = datetime.datetime.now()
        dateString = str(currentDate.year)+"-" + \
            str(currentDate.month) + "-" + str(currentDate.day)
        db = TinyDB("db" + dateString + ".json")
        dateString = dateString
    method = request.method
    args = request.args.to_dict(flat=False)
    headers = dict(request.headers)
    body = request.get_json()
    response = requests.request(method, os.environ["API_TO_WATCH"]+path, params=args,
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
    if "Transfer-Encoding" in response_headers:
        del response_headers["Transfer-Encoding"]
    if "Content-Encoding" in response_headers:
        del response_headers["Content-Encoding"]
    result.headers = response_headers
    return result


serve(app, host="0.0.0.0", port="8000")
