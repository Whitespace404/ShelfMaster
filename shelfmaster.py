from flask import Flask, render_template, flash, redirect, url_for
from flask_login import (
    LoginManager,
    login_user,
    UserMixin,
    login_required,
    logout_user,
    current_user,
)
from flask_sqlalchemy import SQLAlchemy
from forms import BorrowForm, ReturnForm, LoginForm
import sqlalchemy as sa
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config["SECRET_KEY"] = "28679ae72d9d4c7b0e93b1db218426a6"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"


class User(db.Model, UserMixin):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    username = sa.Column(sa.String(20), nullable=False)
    password = sa.Column(sa.String(64), nullable=False)
    borrowed_book_id = relationship("Book", backref="user", lazy=True)

    def __repr__(self):
        return f"ID: {str(self.id)} --- {self.username}"


class Book(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    book_id = sa.Column(sa.Integer)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))

    def __repr__(self):
        return f"#{str(self.id)} -- BOOK: {str(self.book_id)} is borrowed by USER: {str(self.user_id)}"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    form = BorrowForm()

    if form.validate_on_submit():
        u = User.query.filter_by(username=form.usn.data).first()
        if not u:
            u = User(username=form.usn.data, password="test")
            db.session.add(u)
            db.session.commit()
        b = Book(book_id=form.book_id.data, user_id=u.id)
        db.session.add(u)
        db.session.commit()
        db.session.add(b)
        db.session.commit()
        flash(f"Book {form.book_id.data} borrowed successfully.")
        return redirect(url_for("home"))
    return render_template("borrow.html", form=form)


@app.route("/return", methods=["GET", "POST"])
def return_():
    form = ReturnForm()

    if form.validate_on_submit():
        b = Book.query.filter_by(book_id=form.book_id.data).first()
        u = User.query.filter_by(id=b.user_id).first()
        b.user_id = None

        db.session.add(b)
        db.session.commit()

        flash(f"Book taken by {u.username} was returned successfully.")
        return redirect(url_for("home"))

    return render_template("return.html", form=form)


@app.route("/add_user/<u>")
@login_required
def add_user(u=None):
    user = User(username=u, password="test")
    db.session.add(user)
    db.session.commit()

    print(user.id)

    return render_template("success.html", user=user)


@app.route("/view_user/<u>")
@login_required
def view_user(u=None):
    u = User.query.filter_by(username=u).first()

    return render_template("success.html", user=u)


@app.route("/view_book/<id>")
@login_required
def view_book(id=None):
    b = Book.query.filter_by(book_id=id).first()
    usn = User.query.filter_by(id=b.user_id).first()

    borrower = usn
    this = borrower
    return render_template("show_this.html", this=this)


@app.route("/view_books")
@login_required
def view_books():
    books = Book.query.filter_by().all()
    d = dict()
    for book in books:
        borrower = User.query.filter_by(id=book.user_id).first()
        try:
            d[book.book_id] = borrower.username
        except AttributeError:
            d[
                book.book_id
            ] = ""  # TODO Make this actually be NONE in the database if it is not borrowed
    print(d)
    return render_template("books.html", books=d)


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        if form.password.data == "test":
            admin = User.query.filter_by(username="ADMIN").first()
            login_user(admin)
            flash("Logged in.")
            return redirect(url_for("home"))
    return render_template("admin_login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("home"))


# with app.app_context():
#     db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
