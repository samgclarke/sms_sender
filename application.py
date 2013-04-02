#!/usr/bin/env python
import os
from functools import wraps
from flask import Flask, flash, request, render_template, session, Response
import logging
import datetime
from logging.handlers import RotatingFileHandler
from twilio.rest import TwilioRestClient
# app specifi imports
from forms import SMSForm


# fLASK APP
# ############################################################## #
app = Flask(__name__)
app.debug = True
app.secret_key = 'teddymonkey'


# TWILIO
# ############################################################## #
account = "AC16a50fa652a7f11dca5ced009621b1ae"
token = "76df09164e10f60ef38479b4c69dab71"
client = TwilioRestClient(account, token)


# LOGGING
# ############################################################### #
LOG_FILENAME = 'app_access_logs.log'
app.logger.setLevel(logging.INFO)  # use the native logger of flask
handler = RotatingFileHandler(
    LOG_FILENAME,
    maxBytes=1024 * 1024 * 100,
    backupCount=20
)
app.logger.addHandler(handler)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


# VIEWS
# ############################################################### #
@app.route('/', methods=['GET', 'POST'])
@login_required
def hello_world():
    form = SMSForm(request.form)
    if request.method == 'POST' and form.validate():
        to_number = form.number.data
        message = form.message.data
        client.sms.messages.create(
            to=str(to_number),
            from_="+16042274478",
            body=str(message)
        )
        flash('Your SMS message has been sent!')
        app.logger.info('\t'.join([
            datetime.datetime.today().ctime(),
            request.remote_addr,
            request.method,
            request.url,
            request.data,
            to_number,
            message
        ]))
    return render_template(
        'index.html',
        form=form,
    )


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
