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
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime

from forms import BorrowForm, ReturnForm, LoginForm
from admin_forms import AddAdminsForm, AddBookForm, AddUserForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "28679ae72d9d4c7b0e93b1db218426a6"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"


class User(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    username = sa.Column(sa.String(20), nullable=False)
    name = sa.Column(sa.String(32))
    is_teacher = sa.Column(sa.Boolean)
    class_section = sa.Column(sa.String(10))
    borrowed_entities = relationship("Entity", backref="user", lazy=True)

    def __repr__(self):
        return f"ID: {str(self.id)}; {self.username}"


class Admin(db.Model, UserMixin):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    username = sa.Column(sa.String(40), nullable=False)
    password = sa.Column(sa.String(64), nullable=False)

    def __repr__(self):
        return f"{str(self.id)}. {self.username} with {self.password}"


class AdminActionsLog(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    username = sa.Column(sa.String(20))
    action = sa.Column(sa.String(120))
    time = sa.Column(sa.DateTime, default=datetime.now)

    def __repr__(self):
        return f"{self.username} performed {self.action}"


class Entity(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    type = sa.Column(sa.String(40))
    title = sa.Column(sa.String(100))
    author = sa.Column(sa.String(100))
    rack_number = sa.Column(sa.String(20))
    shelf_number = sa.Column(sa.String(20))
    accession_number = sa.Column(sa.String(25))
    call_number = sa.Column(sa.String(32))
    publisher = sa.Column(sa.String(120))
    isbn = sa.Column(sa.Integer)
    vendor = sa.Column(sa.String(32))
    bill_number = sa.Column(sa.String(32))
    amount = sa.Column(sa.String(10))
    remarks = sa.Column(sa.String(120))
    language = sa.Column(sa.String(32))
    is_borrowed = sa.Column(sa.Boolean, default=False)
    due_date = sa.Column(sa.DateTime)
    date_added = sa.Column(sa.DateTime, default=datetime.now)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))

    def __repr__(self):
        return f"{self.id} borrowed by {self.user_id}"


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


@app.route("/")
def home():
    if current_user.is_authenticated:
        return render_template("admin_tools.html")
    return render_template("home.html")


@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    form = BorrowForm()

    if form.validate_on_submit():
        u = User.query.filter_by(username=form.usn.data).first()
        if u is None:
            form.usn.errors.append("USN does not exist")
            return render_template("borrow.html", form=form)

        entity = Entity.query.filter_by(call_number=form.book_id.data).first()
        if entity is None:
            form.book_id.errors.append("That book doesn't exist in the database yet.")
            return render_template("borrow.html", form=form)
        entity.user = u
        entity.is_borrowed = True
        type_of_entity = entity.type

        db.session.add(entity)
        db.session.commit()

        flash(f"{type_of_entity} borrowed successfully.")
        return redirect(url_for("home"))
    return render_template("borrow.html", form=form)


@app.route("/return", methods=["GET", "POST"])
def return_():
    form = ReturnForm()

    if form.validate_on_submit():
        b = Entity.query.filter_by(call_number=form.book_id.data).first()
        former_borrower = b.user
        b.is_borrowed = False
        b.user = None

        db.session.commit()

        flash(f"Book borrowed by {former_borrower} was returned successfully.")
        return redirect(url_for("home"))

    return render_template("return.html", form=form)


@app.route("/add_admin", methods=["GET", "POST"])
@login_required
def add_admin():
    form = AddAdminsForm()
    if form.validate_on_submit():
        admin = Admin(username=form.username.data, password=form.password.data)
        db.session.add(admin)
        db.session.commit()

        performed_action = f"Added a new admin with username '{form.username.data}'"
        action = AdminActionsLog(
            username=current_user.username, action=performed_action
        )
        db.session.add(action)
        db.session.commit()
        flash(f"Admin {admin.username} added successfully.")
        return redirect(url_for("home"))
    return render_template("add_admin.html", form=form)


@app.route("/add_user", methods=["GET", "POST"])
@login_required
def add_user():
    form = AddUserForm()

    if form.validate_on_submit():
        is_teacher = True if form.is_teacher.data == "Teacher" else False
        user = User(
            username=form.username.data,
            name=form.name.data,
            is_teacher=is_teacher,
            class_section=form.class_section.data,
        )
        db.session.add(user)
        db.session.commit()

        performed_action = f"Added a new user with username '{form.username.data}'"
        action = AdminActionsLog(
            username=current_user.username, action=performed_action
        )
        db.session.add(action)
        db.session.commit()

        flash(f"Added user {form.name.data}")
        return redirect(url_for("home"))
    return render_template("add_user.html", form=form)


@app.route("/view_all_users")
@login_required
def view_all_users():
    logs = User.query.filter_by().all()
    return render_template("view_users.html", logs=logs)


@app.route("/view_admin_log")
@login_required
def view_admin_log():
    logs = AdminActionsLog.query.filter_by().all()
    return render_template("admin_log.html", logs=logs)


@app.route("/view_books")
@login_required
def view_books():
    books = Entity.query.filter_by().all()
    return render_template("view_entities.html", books=books)


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin is None:
            flash("Incorrect username/password", "alert")
        elif form.password.data == admin.password:
            login_user(admin)
            log = AdminActionsLog(username=form.username.data, action="Logged in")
            db.session.add(log)
            db.session.commit()
            flash(f"Logged in")
            return redirect(url_for("home"))
    return render_template("admin_login.html", form=form)


@app.route("/add_entity", methods=["GET", "POST"])
@login_required
def add_entity():
    form = AddBookForm()
    if form.validate_on_submit():
        e = Entity(
            type=form.type.data,
            title=form.title.data,
            rack_number=form.rack_number.data,
            shelf_number=form.shelf_number.data,
            accession_number=form.accession_number.data,
            call_number=form.call_number.data,
            publisher=form.publisher.data,
            isbn=form.isbn.data,
            vendor=form.vendor.data,
            bill_number=form.bill_number.data,
            amount=form.amount.data,
            remarks=form.remarks.data,
            language=form.language.data,
        )
        db.session.add(e)
        db.session.commit()

        log_message = f"Added a {form.type.data} with Call Number:{form.call_number.data}"  # NOTE here as well :)
        action = AdminActionsLog(username=current_user.username, action=log_message)
        db.session.add(action)
        db.session.commit()

        flash(f"{form.type.data} added successfully")
        return redirect(url_for("home"))
    return render_template("add_entity.html", form=form)


@app.route("/logout")
@login_required
def logout():
    log = AdminActionsLog(username=current_user.username, action="Logged out")
    db.session.add(log)
    db.session.commit()
    logout_user()
    flash("Logged out")
    return redirect(url_for("home"))


# with app.app_context():
#     db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
