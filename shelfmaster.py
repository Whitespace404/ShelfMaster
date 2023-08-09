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
        return str(self.id) + self.username + self.borrowed_book_id


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    form = BorrowForm()

    if form.validate_on_submit():
        u = User(
            username=form.usn.data, password="test", borrowed_book_id=form.book_id.data
        )
        db.session.add(u)
        db.session.commit()
        flash(f"Book {form.book_id.data} borrowed successfully.")
        return redirect(url_for("home"))
    return render_template("borrow.html", form=form)


@app.route("/return", methods=["GET", "POST"])
def return_():
    return render_template("return.html")


@app.route("/add_user/<u>")
def add_user(u=None):
    user = User(username=u, password="sup")
    db.session.add(user)
    db.session.commit()

    print(user.id)

    return render_template("success.html", user=user)


@app.route("/view_user/<u>")
def view_user(u=None):
    u = User.query.filter_by(username=u).first()

    return render_template("success.html", user=u)


if __name__ == "__main__":
    app.run(debug=True)
