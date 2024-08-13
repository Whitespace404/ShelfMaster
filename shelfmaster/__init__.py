from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "cx8z315xS3V6HxsP1msE6diwAHGCqHRDY1lyGoBvuguX2"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"
app.config["UPLOAD_EXTENSIONS"] = [".xls", ".xlsx"]
app.config["UPLOAD_PATH"] = "uploads"

db = SQLAlchemy(app)
login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = "admin_login"


from shelfmaster import routes
