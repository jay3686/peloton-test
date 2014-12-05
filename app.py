import os
from simplejson import JSONDecodeError
from requests import HTTPError
from flask import Flask
from flask import request
from flask import jsonify
app = Flask(__name__)
import requests
DEBUG_MODE = False


class MergedStream:
    BASE_STREAM_URL = 'https://api.pelotoncycle.com/quiz/next/%s'

    def __init__(self, first, second):
        self.first_stream = first
        self.second_stream = second
        self.first_top = None
        self.second_top = None
        self.last = None

    def next(self):
        if self.first_top is None:
            self.first_top = self.next_from_stream(self.first_stream)
        if self.second_top is None:
            self.second_top = self.next_from_stream(self.second_stream)

        if self.first_top <= self.second_top:
            next_val = self.first_top
            self.first_top = None
        else:
            next_val = self.second_top
            self.second_top = None

        ret_val = {'current': next_val, 'last': self.last}
        self.last = next_val
        return ret_val

    def next_from_stream(self, stream):
        if DEBUG_MODE:
            print stream
        stream_url = self.BASE_STREAM_URL % stream
        try:
            res = requests.get(stream_url)
            if res.status_code != 200:
                raise HTTPError
            return res.json()['current']
        except (HTTPError, JSONDecodeError, KeyError):
            raise Exception('Error getting next element in stream %s' % stream)

# In a production environment this would be some kind of web server
# or distributed cache.
lazy_stream_cache = {}


@app.route('/')
def hello_world():

    return 'Hi! This is a test task from PelotonCycle'


@app.route('/quiz/next')
def merge():

    if request.method != 'GET':
        return jsonify({'error': 'this endpoint only accepts GETs'})
    try:
        stream1 = request.args['stream1']
        stream2 = request.args['stream2']
    except KeyError:
        return jsonify({'error': 'stream arguments not passed'})
    try:
        m = lazy_stream_cache[stream1, stream2]
    except KeyError:
        m = MergedStream(stream1, stream2)
        lazy_stream_cache[stream1, stream2] = m

    try:
        return jsonify(m.next())
    except Exception, e:
        # in prod environment log this or send an alert
        return jsonify({'error': e.message})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG_MODE)
