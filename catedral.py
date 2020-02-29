import logging

from flask import Flask
from flask_ask import Ask, statement

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def news():
    welcome_msg = render_template('welcome')
    