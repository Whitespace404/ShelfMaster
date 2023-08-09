from flask import Flask, render_template, flash, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from forms import BorrowForm
import sqlalchemy as sa

app = Flask(__name__)
app.config["SECRET_KEY"] = "28679ae72d9d4c7b0e93b1db218426a6"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"


db = SQLAlchemy(app)


class User(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(20), unique=True, nullable=False)
    password = sa.Column(sa.String(64), nullable=False)
    borrowed_book_id = sa.Column(sa.String(25))

    def __repr__(self):
        return self.id + self.username


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    form = BorrowForm()

    if form.validate_on_submit():
        flash(f"Book {form.book_id.data} borrowed successfully.")
        return redirect(url_for("home"))
    return render_template("borrow.html", form=form)


@app.route("/return", methods=["GET", "POST"])
def return_():
    return render_template("return.html")


@app.route("/add_user/<u>")
def add_user(u="sup"):
    user = User(username=u, password="sup")
    db.session.add(user)
    db.session.commit()

    print(user.id)

    return render_template("success.html", id=user.id)


if __name__ == "__main__":
    app.run(debug=True)
