from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS

from bannedWordServer.config import DB_LOCATION, SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DB_LOCATION
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)

db = SQLAlchemy(app)