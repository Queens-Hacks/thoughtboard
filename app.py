#!/usr/bin/env python
import os
from flask import Flask,request, redirect
import twilio.twiml

app = Flask(__name__)


getenv = lambda *names: {v: os.environ.get(v) for v in names}
app.config.update(**getenv(
    'AUTH_TOKEN',
    'CELL_NUM',
    'MONGOLAB_URI',
    'TWILLIO_NUM',
))


@app.route('/sms', methods=['GET','POST'])
def send_sms():
    from_number = request.values.get('From', None)
    message="Hey there"
    resp = twilio.twiml.Response()
    resp.message(message)
 
    return str(resp)


if __name__ == '__main__':
    app.run(debug=True)
