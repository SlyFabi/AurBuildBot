from flask import Flask
from flask_httpauth import HTTPBasicAuth
from Bot.Bot import Bot

BOT = Bot()

APP = Flask(__name__)
APP_AUTH = HTTPBasicAuth()
