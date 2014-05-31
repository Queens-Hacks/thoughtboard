#!/usr/bin/env python
import os
from flask import Flask

app = Flask(__name__)


getenv = lambda *names: {v: os.environ.get(v) for v in names}
app.config.update(**getenv(
    'AUTH_TOKEN',
    'CELL_NUM',
    'MONGOLAB_URI',
    'TWILLIO_NUM',
))


@app.route('/')
def home():
    return "yo"


if __name__ == '__main__':
    app.run(debug=True)
