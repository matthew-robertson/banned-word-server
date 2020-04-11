import os

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.environ['DB_LOCATION']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
CORS(app)

db = SQLAlchemy(app)