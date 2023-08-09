from flask import Flask, render_template, flash, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from forms import BorrowForm


app = Flask(__name__)
app.config["SECRET_KEY"] = "28679ae72d9d4c7b0e93b1db218426a6"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    borrowed_book = db.relationship("Book", backref="borrower", lazy=True)

    def __repr__(self):
        return self.id + self.username


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return self.title + " borrowed by " + self.user_id


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    form = BorrowForm()

    if form.validate_on_submit():
        flash("Book borrowed successfully.")
        return redirect(url_for("home"))
    return render_template("borrow.html", form=form)


@app.route("/return", methods=["GET", "POST"])
def return_():
    return render_template("return.html")


app.run(debug=True)
