from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)

# There's probably a different way we're supposed to do this that's more secure?
app.config['SECRET_KEY'] = 'tskdgjhuiae374rteh78qt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db.init_app(app)

from .models import Mood, Website
from app import views
