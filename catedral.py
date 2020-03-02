import logging

from flask import Flask
from flask_ask import Ask, statement

app = Flask(__name__)

ask = Ask(app, "/catedral")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def news():
    welcome_msg = 'Bem-vindo'
    return statement(welcome_msg)
    