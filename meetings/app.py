from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite'

db = SQLAlchemy(app)

limiter = Limiter(app, key_func=get_remote_address, default_limits=["100 per minute"])

from routes import *  # noqa: E402, F401

db.create_all()
