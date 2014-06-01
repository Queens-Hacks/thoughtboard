#!/usr/bin/env python
import os
import random
from datetime import datetime, timedelta
import twilio.twiml
from flask import Flask, request
from flask.ext.pymongo import PyMongo, DESCENDING

app = Flask(__name__)


CONFIGS = (
    'AUTH_TOKEN',
    'CELL_NUM',
    'MONGOLAB_URI',
    'TWILIO_NUM',
)


# Set up the app
app = Flask(__name__)
app.config.update(DEBUG=(os.environ.get('DEBUG') == 'TRUE'))
app.config.update(**{v: os.environ[v] for v in CONFIGS})
app.config['MONGO_URI'] = app.config['MONGOLAB_URI']  # for flask-pymongo


# Initialize extensions
pymongo = PyMongo(app)


# Some constants
SMS_CODE_RESET = timedelta(seconds=30)
SMS_CODE_GRACE = timedelta(seconds=15)
USER_CHECKIN_EXPIRE = timedelta(minutes=15)
USER_POST_THROTTLE = timedelta(seconds=10)


"""Collection schemas

users: {
    phone_number: string
    created: datetime
    last_checkin: datetime
}

codes: {
    code: string
    created: datetime
}

posts: {
    message: string
    poster_id: user_id
    submitted: datetime
    showtime: datetime  # not present if it hasn't been shown yet
    extender_ids: [user_ids]
}
"""


class InvalidCodeException(Exception):
    """When user uses code that doesn't exist"""

class NotCheckedInException(Exception):
    """When user tries to vote or post before checking in"""


class ChillOut(Exception):
    """When users get too excited (try to re-up-vote or re-post too soon)."""


def notz(dt):
    """Remove the timezone info from a datetime object"""
    return dt.replace(tzinfo=None)


def create_sms_code():
    """Create a new code. More races woo!"""
    while True:
        code = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz1234567890') for _ in range(6))
        existing_with_code = pymongo.db.codes.find_one({'code': code})
        if existing_with_code is None:
            break

    new_sms = {
        'code': code,
        'created': datetime.now()
    }
    pymongo.db.codes.insert(new_sms)
    return new_sms


def get_sms_code():
    """Fetches the most up-to-date SMS code for the billboard.

    This may trigger a new code if one is due.
    """
    codes = pymongo.db.codes.find().sort('created', DESCENDING)
    try:
        current = next(codes)
    except StopIteration:  # empty database
        current = create_sms_code()
    if notz(current['created']) + SMS_CODE_RESET < datetime.now():
        # yo, WARNING: off to the races!
        current = create_sms_code()
    return current['code']


def check_sms_code(test_code):
    """Checks whether the SMS code is currently valid."""
    codes = pymongo.db.codes.find().sort('created', DESCENDING)
    current = next(codes)
    if test_code == current['code']:
        return True
    else:
        previous = next(codes)
        if (test_code == previous['code'] and
            datetime.now() - notz(current['created']) < SMS_CODE_GRACE):
            return True
        else:
            return False


def get_queue():
    """Fetch all posts currently queued."""
    unshown = pymongo.db.posts.find({'showtime': {'$exists': False}})
    queue_in_order = unshown.sort('submitted')
    return queue_in_order


def get_user_from_phone(phone_number):
    """Get a user given their phone number, or None if they don't exist"""
    return pymongo.db.users.find_one({'phone_number': phone_number})


def is_checked_in(user):
    """Test whether a user is checked in or not."""
    if user is None:
        return False
    a_ok = notz(user['last_checkin']) + USER_CHECKIN_EXPIRE > datetime.now()
    return a_ok


def check_in_with_sms_code(phone_number, code):
    """Check in (and possibly create) a user, verified by the active code.

    Returns the user's data, or raises InvalidCodeException if the code is wrong or expired.
    """
    if not check_sms_code(code):
        raise InvalidCodeException("You fucked up")
    user = pymongo.db.users.find_one({'phone_number': phone_number})
    if user is None:  # so racey
        user = {
            'phone_number': phone_number,
            'created': datetime.now(),
        }
    user['last_checkin'] = datetime.now()
    pymongo.db.users.save(user)
    return user


def get_current_post():
    showing = pymongo.db.posts.find_one({'showtime': {'$exists': True}},
                                        sort=[('showtime', DESCENDING)])
    return showing


def post_message(user, message):
    """Try to queue a message for a user.

    Returns the message's position in the queue.

    Raises ChillOut if the user has posted too many messages recently.
    """
    user_id = user['_id']
    prev = pymongo.db.posts.find_one({'poster_id': user_id},
                                     sort=[('submitted', DESCENDING)])
    if (prev is not None and
        notz(prev['submitted']) + USER_POST_THROTTLE < datetime.now()):
        raise ChillOut('Whoa. Chill out, hey. So many messages.')

    post = {
        'message': message,
        'poster_id': user_id,
        'submitted': datetime.now(),
        'extenders': [user_id],
    }
    pymongo.db.posts.insert(post)
    return len(get_queue())


def save_vote(user):
    """Register a vote for a user.

    Returns 1 if the vote was counted.
    Raises ChillOut if the user has already voted for the showing post.

    Currently it is hard-coded to always succeed
    """

    current_post = get_current_post();
    pymongo.db.posts.update({"_id": current_post["_id"]},{ "$addToSet":user["_id"]});
    return 1


@app.route('/sms', methods=['GET','POST'])
def handle_sms():

    #Get number and response
    from_number = request.values.get('From', None)
    from_response = request.values.get('Body',None)
    first_word = from_response.lower().split(' ',1)[0];
    resp = twilio.twiml.Response()

    user = get_user_from_phone(from_number)

    #Checks if user already checked in

    if is_checked_in(user):
         #Check if user response is vote
        if "vote" in first_word:
            if save_vote(user):
                message="Vote successful"
            else:
                message="Vote unsuccessful"

        #Check if user response is a post
        elif "post" in first_word:
            queue_num = post_message(user, from_response.lower().split(' ',1)[1])
            message = "Your message is queued in position {}".format(queue_num)

        else:
            #check if code is correct
            try:
                check = check_in_with_sms_code(from_number, from_response);

            except InvalidCodeException:
                #error handling
                message="fucked up"
                resp.message(message)
                return str(resp)

            message = ''' Thanks for checking in! To vote, Please
            text 'vote', otherwise text 'post' and type in your message '''

    #User hasn't checked in but is checking in now
    elif "post" not in first_word and "vote" not in first_word:
          #check if code is correct
            try:
                check = check_in_with_sms_code(from_number, from_response);

            except InvalidCodeException:
                #error handling
                message="fucked up"
                resp.message(message)
                return str(resp)

            message = ''' Thanks for checking in! To vote, Please
            text 'vote', otherwise text 'post' and type in your message '''
    else:
        #error handling
        message="Not checked in"
        resp.message(message)
        return str(resp)


    resp.message(message)

    return str(resp)


@app.route('/')
def home():
    message = get_current_post() or 'No post yet :('
    return message


# dev stuff

def push():
    """Push a test request context"""
    ctx = app.test_request_context()
    ctx.push()
    return ctx


if __name__ == '__main__':
    app.run(debug=True)
