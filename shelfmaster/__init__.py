from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SECRET_KEY"] = "cx8z315xS3V6HxsP1msE6diwAHGCqHRDY1lyGoBvuguX2"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"
app.config["UPLOAD_EXTENSIONS"] = [".xls", ".xlsx"]
app.config["UPLOAD_PATH"] = "uploads"
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager()
migrate = Migrate(app, db)

login_manager.init_app(app)
login_manager.login_view = "admin_login"

from shelfmaster import routes
