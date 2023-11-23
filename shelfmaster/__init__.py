import os
from dotenv import load_dotenv

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

app = Flask(__name__)
app.config["SECRET_KEY"] = "cx8z351TS3V6HxsP1msE6ldiweAHGCqHRDYyGoBvuguX2LPs"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"

load_dotenv()
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
mail.init_app(app)
login_manager.login_view = "admin_login"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "severusvirtanen@gmail.com"
app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

from shelfmaster import routes
