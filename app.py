from simplejson import JSONDecodeError
from requests import HTTPError
from flask import Flask
from flask import request
app = Flask(__name__)
import requests
DEBUG_MODE = TRUE


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

        if (self.first_top is not None and
                self.first_top <= self.second_top or
                self.second_top is None):
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

m = MergedStream('foo', 'bar')


@app.route('/')
def hello_world():

    while True:
        v = m.next()
        print v
        if not v:
            break

    return 'Hi! This is a test task from PelotonCycle'

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE)
