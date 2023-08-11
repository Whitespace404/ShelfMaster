from flask import Flask, render_template, flash, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from forms import BorrowForm
import sqlalchemy as sa
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config["SECRET_KEY"] = "28679ae72d9d4c7b0e93b1db218426a6"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"


db = SQLAlchemy(app)


class User(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    username = sa.Column(sa.String(20), nullable=False)
    password = sa.Column(sa.String(64), nullable=False)
    borrowed_book_id = relationship("Book", backref="user", lazy=True)

    def __repr__(self):
        return str(self.id) + self.username + self.borrowed_book_id


class Book(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    book_id = sa.Column(sa.Integer)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return str(self.id) + str(self.book_id) + "borrowed by" + str(self.user_id)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    form = BorrowForm()

    if form.validate_on_submit():
        u = User(
            username=form.usn.data, password="test"
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
    user = User(username=u, password="test")
    db.session.add(user)
    db.session.commit()

    print(user.id)

    return render_template("success.html", user=user)


@app.route("/view_user/<u>")
def view_user(u=None):
    u = User.query.filter_by(username=u).first()

    return render_template("success.html", user=u)


@app.route('/add_book/<book_id>')
def add_book(book_id=55):
    b = Book(book_id=int(book_id))
    db.session.add(b)
    db.session.commit()

    flash('Book borrowed succesfully')
    return redirect('home.html')


# Initialise the database
# with app.app_context():
#     db.create_all()


'''
with app.app_context():
    u = User(
        username="100N006",
        password="ter",
    )

    db.session.add(u)
    db.session.commit()

    print(u.id)

    b = Book(book_id=50, user_id=u.id)
    db.session.add(b)
    db.session.commit()

    print(u.borrowed_book_id)
'''

if __name__ == "__main__":
    app.run(debug=True)
