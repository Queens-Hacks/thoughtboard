#!/usr/bin/env python
import os
import twilio.twiml
from flask import Flask, request
from flask.ext.pymongo import PyMongo

app = Flask(__name__)


CONFIGS = (
    'AUTH_TOKEN',
    'CELL_NUM',
    'MONGOLAB_URI',
    'TWILIO_NUM',
)


# Set up the app
app = Flask(__name__)
app.config.update(**{v: os.environ[v] for v in CONFIGS})
app.config['MONGO_URI'] = app.config['MONGOLAB_URI']  # for flask-pymongo


# Initialize extensions
pymongo = PyMongo(app)


def check_in(phone_number, code):
    """Check in (and possibly create) a user, verified by the active code.

    Returns the user's data, or None if the code is wrong.

    The correct code is currently hard-coded to ABC.
    """
    user_data = {
        'phone_number': phone_number
    }
    return user_data if code == 'ABC' else None


@app.route('/sms', methods=['GET','POST'])
def send_sms():
    from_number = request.values.get('From', None)
    message="Hey there"
    resp = twilio.twiml.Response()
    resp.message(message)

    return str(resp)


if __name__ == '__main__':
    app.run(debug=True)
