from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "cx8z351TS3V6HxsP1msE6ldiweAHGCqHRDYyGoBvuguX2LPs"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"

from shelfmaster import routes
