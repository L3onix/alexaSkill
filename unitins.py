from flask import Flask
from flask_ask import Ask, statement, request, context, question, session, convert_errors, version
import json
import requests
import time
import unidecode
import lxml.html as html
import pandas as pd
import random
from util.util import match_value, scraping_table_as_dataframe, contato_format_msg

## https://developer.amazon.com/en-US/docs/alexa/alexa-design/adaptable.html

app = Flask(__name__)
ask = Ask(app, "/unitins")

def get_news():
    pass

def get_telefone(contato):
    fone = "3 2 1 8 29 49"
    url = "https://www.unitins.br/nportal/portal/page/show/contatos-da-unitins"
    
    contatos = scraping_table_as_dataframe(url)

    eleito = match_value(contatos, contato)

    msg = contato_format_msg(eleito)
    
    return msg

@app.route("/")
def homepage():
    return "Olá, Mundo!"

@ask.launch
def start_skill():
    welcome_message = "E aí meu querido, o que posso fazer por você?"
    return question(welcome_message).reprompt("Consigo acessar os contatos, abrir um chamado no iProtocolo e outras coisas mais.")


@ask.intent('AgeIntent', convert={'age': int})
def say_age(age):
    frases_duvida = ["Poderia repetir sua idade?",
                    "Qual é mesmo sua idade?"]

    frases_solicitar_idade = [  "Poderia me contar sua idade?",
                                "Qual é sua idade?",
                                "Quantos anos você tem?"]
    
    frases_resposta = [ "Você possui {} anos.",
                        "Você tem {} anos.",
                        "Você possui apenas {} primaveras"]

    if 'age' in convert_errors:
        return question(random.choice(frases_duvida))
    
    if age is None:
        return question(random.choice(frases_solicitar_idade))

    return statement(random.choice(frases_resposta).format(age))


@ask.intent("iProtocoloIntent")
def iprotocolo():
    return question("Ummmm.. vamos lá então. Qual é sua solicitação?")

@ask.intent("ContatosIntent", convert={'contato': str})
def contatos(contato):

    if 'contato' in convert_errors:
        return question("Número de quem mesmo?")
    
    if contato is None:
        return question("Devo procurar o telefone de quem ou de onde mesmo?")
    
    fone = get_telefone(contato)
    print(fone)

    return statement(fone)

@ask.intent('AMAZON.StopIntent')
def stop():
    return statement("Até mais")


@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement("Até mais")


@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == "__main__":
    app.run(debug=True)