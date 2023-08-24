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

from datetime import datetime, timedelta

from forms import BorrowForm, ReturnForm, LoginForm
from admin_forms import AddAdminsForm, AddBookForm, AddUserForm

# from excel_automation import read_file_and_get_details, read_namelist_and_get_details
from helper_functions import exceeds_seven_days

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


class TransactionLog(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    user_id = sa.Column(sa.Integer)
    entity_id = sa.Column(sa.Integer)
    borrowed_time = sa.Column(sa.DateTime, default=datetime.now)
    due_date = sa.Column(
        sa.DateTime, default=lambda: datetime.now() + timedelta(days=7)
    )

    def __repr__(self):
        return f"{str(self.id)}"


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
    place_of_publication = sa.Column(sa.String(64))
    isbn = sa.Column(sa.String(20))
    vendor = sa.Column(sa.String(32))
    bill_number = sa.Column(sa.String(32))
    bill_date = sa.Column(sa.DateTime)
    amount = sa.Column(sa.String(10))
    remarks = sa.Column(sa.String(120))
    language = sa.Column(sa.String(32))
    is_borrowed = sa.Column(sa.Boolean, default=False)
    due_date = sa.Column(sa.DateTime)
    date_added = sa.Column(sa.DateTime, default=datetime.now)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))

    def __repr__(self):
        return f"{self.accession_number}"


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

        entity = Entity.query.filter_by(accession_number=form.book_id.data).first()
        if entity is None:
            form.book_id.errors.append("That book doesn't exist in the database yet.")
            return render_template("borrow.html", form=form)
        if not entity.is_borrowed:
            entity.user = u
            entity.is_borrowed = True
            type_of_entity = entity.type

            log = TransactionLog(user_id=u.id, entity_id=entity.id)
            db.session.add(log)
            db.session.commit()

        else:
            form.book_id.errors.append(
                f"This book is already borrowed by {entity.user.name}."
            )
            return render_template("borrow.html", form=form)

        db.session.add(entity)
        db.session.commit()

        flash(f"{type_of_entity} borrowed successfully.")
        return redirect(url_for("home"))
    return render_template("borrow.html", form=form)


@app.route("/return", methods=["GET", "POST"])
def return_():
    form = ReturnForm()

    if form.validate_on_submit():
        b = Entity.query.filter_by(accession_number=form.book_id.data).first()
        if b is None:
            form.book_id.errors.append("That book doesn't exist in the database.")
            return render_template("return.html", form=form)
        if b.user is None:
            form.book_id.errors.append("That book is not borrowed.")
            return render_template("return.html", form=form)

        t = TransactionLog.query.filter_by(
            entity_id=b.id, user_id=b.user.id
        ).first()  # TODO does .first() pose a problem here when multiple books borrowed? use .last() instead??

        current_dt = datetime.now()
        if not exceeds_seven_days(current_dt, t.borrowed_time):
            former_borrower = b.user
            b.is_borrowed = False
            b.user = None
            flash(f"Book borrowed by {former_borrower.name} was returned successfully.")
        else:
            former_borrower = b.user
            b.is_borrowed = False
            b.user = None
            flash(f"Book borrowed by {former_borrower.name} was returned successfully.")
            flash(f"Fine must be paid by {former_borrower.name} ", "alert")
        db.session.commit()
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


@app.route("/view_transactions")
def view_transactions():
    transactions = TransactionLog.query.filter_by().all()

    return render_template("view_transaction_log.html", transactions=transactions)


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
            place_of_publication=form.place_of_publication.data,
            isbn=form.isbn.data,
            vendor=form.vendor.data,
            bill_number=form.bill_number.data,
            amount=form.amount.data,
            remarks=form.remarks.data,
            language=form.language.data,
        )
        db.session.add(e)
        db.session.commit()

        log_message = f"Added a {form.type.data} with Accession Number:{form.accession_number.data}"
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


@app.route("/create_db")
def create_db():
    db.create_all()

    admin = Admin(username="rahulreji", password="power")
    db.session.add(admin)
    db.session.commit()

    # for t in read_namelist_and_get_details():
    #     u = User(username=t[0], name=t[1], is_teacher=False, class_section="4A")
    #     db.session.add(u)
    #     db.session.commit()

    # for v in read_file_and_get_details():
    #     e = Entity(
    #         type="Book",
    #         title=v["title"],
    #         author=v["author"],
    #         accession_number=v["accession_number"],
    #         call_number=v["call_number"],
    #         publisher=v["publisher"],
    #         place_of_publication=v["place_of_publication"],
    #         isbn=v["isbn"],
    #         vendor=v["vendor"],
    #         bill_number=v["bill_number"],
    #         amount=v["price"],
    #         language="English",
    #     )
    #     db.session.add(e)
    #     db.session.commit()

    flash("success")
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
