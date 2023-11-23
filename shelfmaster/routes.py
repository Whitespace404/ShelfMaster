from datetime import datetime, timedelta
from random import randint, choice

from flask import render_template, redirect, request, flash, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from sqlalchemy import func

from shelfmaster import db, app, mail
from shelfmaster.forms import (
    LoginForm,
    BorrowForm,
    ReturnForm,
    ConfirmReturnForm,
    SuggestBookForm,
)
from shelfmaster.admin_forms import (
    AddAdminsForm,
    AddBookForm,
    AddUserForm,
    CatalogForm,
    ReportsForm,
    FineReceivedForm,
    AddHolidayForm,
)
from shelfmaster.models import (
    User,
    Admin,
    Entity,
    TransactionLog,
    AdminActionsLog,
    FinesLog,
    Holidays,
    Suggestions,
)
from shelfmaster.utilities import (
    super_admin_required,
    find_dif,
    borrow_book,
    create_database,
    calculate_overdue_days,
)
from shelfmaster.const import ROLE_PERMS


@app.route("/")
def home():
    if current_user.is_authenticated:
        books = Entity.query.filter_by(type="Book").count()
        transactions = TransactionLog.query.count()
        users = User.query.count()
        return render_template(
            "admin_tools.html",
            title="Admin Tools",
            books=books,
            transactions=transactions,
            users=users,
        )
    return render_template("home.html", title="Home")


@app.route("/borrow/", methods=["GET", "POST"])
def borrow():
    form = BorrowForm()

    if request.method == "GET":
        accession_number = request.args.get("accession_number")

        if accession_number is not None:
            form.book_id.data = accession_number

    if form.validate_on_submit():
        u = User.query.filter_by(username=form.usn.data).first()
        entity = Entity.query.filter_by(accession_number=form.book_id.data).first()

        # age_category = entity.call_number.split("/")[0]

        # ROLE_PERMS.index(age_category)

        # Now find the ROLE PERM of the user using the database
        # and then compare if it is equal or lesser than the
        # previous user and then compile the results
        # GOANBOYLERED

        if u is None:
            form.usn.errors.append("USN does not exist")
            return render_template("borrow.html", form=form, title="Borrow A Book")
        if entity is None:
            form.book_id.errors.append("That book doesn't exist in the database yet.")
            return render_template("borrow.html", form=form, title="Borrow A Book")
        if entity.is_borrowed:
            form.book_id.errors.append(
                f"{form.book_id.data} borrowed by {entity.user.name}."
            )
            return render_template("borrow.html", form=form, title="Borrow A Book")
        if u.is_teacher:
            borrow_book(u, entity)
            flash(f"{entity.type} borrowed successfully.")
            return redirect(url_for("home"))
        elif len(u.borrowed_entities) == 0:
            # if entity.call_number
            borrow_book(u, entity)
            flash(
                f"{entity.type} borrowed successfully. Please return it before {entity.due_date.strftime('%d/%m/%y')}"
            )
            return redirect(url_for("home"))
        else:
            form.usn.errors.append(
                "You have already borrowed a book. -linebreak- Return it and try again. "
            )
    return render_template("borrow.html", form=form, title="Borrow A Book")


@app.route("/return", methods=["GET", "POST"])
@login_required
def return_():
    form = ReturnForm()

    if form.validate_on_submit():
        b = Entity.query.filter_by(accession_number=form.book_id.data).first()
        if b is None:
            form.book_id.errors.append("That book doesn't exist in the database.")
            return render_template("return.html", form=form, title="Return a Book")
        if b.user is None:
            form.book_id.errors.append("That book is not borrowed.")
            return render_template("return.html", form=form, title="Return a Book")

        return redirect(url_for("confirm_return", accession_number=b.accession_number))

    return render_template("return.html", form=form, title="Return a Book")


@app.route("/confirm_return/<accession_number>", methods=["GET", "POST"])
def confirm_return(accession_number):
    # TODO sanitize b here since this route can be accessed without redirect.
    form = ConfirmReturnForm()
    b = Entity.query.filter_by(accession_number=accession_number).first()
    is_fine_needed = None
    current_dt = datetime.now()

    overdue_days = calculate_overdue_days(current_dt, b.due_date)

    if overdue_days is None:  # then that means it was returned before time
        is_fine_needed = False
    else:  # that means there has to be a fine imposed
        # that is only if it is a student (teachers can borrow without a due date)
        # maybe TODO use ^^ to modify overdue function, can prevent this if condition
        if not b.user.is_teacher:
            is_fine_needed = True

    borrowed_time = TransactionLog.query.filter_by(entity_id=b.id).all()
    fine_details = {}

    if is_fine_needed:
        fine_details: dict[str:int] = {
            "days_late": overdue_days,
            "amount": overdue_days * 10,
        }

    if form.validate_on_submit():
        if is_fine_needed:
            fine_amount = overdue_days * 10
            fine = FinesLog(
                user=b.user,
                entity=b,
                due_date=b.due_date,
                date_returned=current_dt,
                days_late=overdue_days,
                fine_amount=fine_amount,
                amount_currently_due=fine_amount,
            )
            db.session.add(fine)
        # return the book, with remarks. must have to make checkout_log work for remarks.
        b.is_borrowed = False
        b.user = None
        b.due_date = None
        b.borrowed_date = None

        db.session.commit()

        flash(f"Book was returned successfully.")
        return redirect(url_for("home"))

    return render_template(
        "confirm_return.html",
        book=b,
        fine_details=fine_details,
        form=form,
        current_date=current_dt,
        borrowed_time=borrowed_time,
        fine_needed=is_fine_needed,
        title="Invoice",
    )


@app.route("/add_admin", methods=["GET", "POST"])
@super_admin_required
def add_admin():
    form = AddAdminsForm()
    if form.validate_on_submit():
        role: int = 2 if form.role.data == "Super-Admin" else 1
        admin = Admin(
            username=form.username.data,
            password=form.password.data,
            role_id=role,
        )
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
    return render_template("add_admin.html", form=form, title="Add an Admin")


@app.route("/add_user", methods=["GET", "POST"])
@login_required
def add_user():
    form = AddUserForm()

    if form.validate_on_submit():
        is_teacher = True if form.is_teacher.data == "Teacher" else False

        u = User.query.filter_by(username=form.username.data).first()
        if u is not None:
            form.username.errors.append("USN already exists.")
            return render_template("add_user.html", form=form, title="Add a User")
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
    return render_template("add_user.html", form=form, title="Add a User")


@app.route("/view_all_users")
@login_required
def view_all_users():
    logs = User.query.filter_by().all()
    return render_template("view_users.html", logs=logs, title="Users List")


@app.route("/view_admin_log")
@super_admin_required
def view_admin_log():
    logs = AdminActionsLog.query.filter_by().all()
    return render_template("admin_log.html", logs=logs, title="Admin Logs")


@app.route("/view_fine_log")
@login_required
def view_fine_log():
    logs = FinesLog.query.filter_by().all()
    return render_template("view_fine_log.html", logs=logs, title="Fine Logs")


@app.route("/view_all_admins")
@login_required
def view_all_admins():
    logs = Admin.query.filter_by().all()
    return render_template("view_admins.html", logs=logs, title="Admin List")


@app.route("/view_books")
@login_required
def view_books():
    books = Entity.query.filter_by().all()
    current_date = datetime.now()
    return render_template(
        "view_entities.html",
        books=books,
        current_date=current_date,
        find_dif=find_dif,
        title="Book List",
    )


@app.route("/view_transactions")
@login_required
def view_transactions():
    transactions = TransactionLog.query.filter_by().all()
    return render_template(
        "view_transaction_log.html", transactions=transactions, title="Transaction Log"
    )


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
            next_page = request.args.get("next")
            return redirect(next_page if next_page else url_for("home"))
        else:
            flash("Incorrect username/password")
            return redirect(url_for("admin_login"))
    return render_template("admin_login.html", form=form, title="Admin Login")


# TODO multistep form here in order to add various types of objects
@app.route("/add_entity", methods=["GET", "POST"])
@super_admin_required
def add_entity():
    form = AddBookForm()
    if form.validate_on_submit():
        e = Entity(
            type=form.type.data,
            title=form.title.data,
            author=form.author.data,
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
    return render_template("add_entity.html", form=form, title="Add an Entity")


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
    create_database()

    flash("Database successfully initialised.")
    return redirect(url_for("home"))


@app.route("/reports", methods=["GET", "POST"])
@login_required
def reports():
    form = ReportsForm()

    if form.validate_on_submit():
        if form.report_type.data == "books":
            most_read_books = (
                db.session.query(
                    Entity, func.count(TransactionLog.id).label("borrow_count")
                )
                .join(TransactionLog)
                .group_by(Entity)
                .order_by(func.count(TransactionLog.id).desc())
                .all()
            )

            if most_read_books:
                return render_template(
                    "book_report.html", rep=most_read_books, title="Reports"
                )
        elif form.report_type.data == "readers":
            most_avid_readers = (
                db.session.query(
                    User, func.count(TransactionLog.id).label("borrow_count")
                )
                .join(TransactionLog)
                .group_by(User)
                .order_by(func.count(TransactionLog.id).desc())
                .all()
            )

            if most_avid_readers:
                return render_template(
                    "readers_report.html", rep=most_avid_readers, title="Reports"
                )
    return render_template("reports_form.html", form=form, title="Generate a Report")


SEARCH_TYPE_MAPPING: dict = {
    "author": Entity.author,
    "title": Entity.title,
    "call_number": Entity.call_number,
    "is_borrowed": Entity.is_borrowed,
    "accession_number": Entity.accession_number,
}


@app.route("/catalog", methods=["GET", "POST"])
def catalog():
    form = CatalogForm()
    if form.validate_on_submit():
        if form.criteria.data in SEARCH_TYPE_MAPPING:
            search_attribute = SEARCH_TYPE_MAPPING[form.criteria.data]
            q = Entity.query.filter(
                search_attribute.ilike(f"%{form.query.data}%")
            ).all()
        else:
            q = []

        if q:
            current_date = datetime.now()

            return render_template(
                "view_entities.html",
                books=q,
                find_dif=find_dif,
                current_date=current_date,
                title="Book list",
            )
        else:
            flash("No results found")
    return render_template("catalog.html", form=form, title="Search")


@app.route("/view_entity/<ac_number>")
def view_entity(ac_number):
    book = Entity.query.filter_by(accession_number=ac_number).first()
    if book:
        borrowers = TransactionLog.query.filter_by(entity=book).all()
        return render_template(
            "view_entity.html",
            book=book,
            e=borrowers,
            title=f"View {book.title} by {book.author}",
        )
    flash(f"Could not find a book with accession number = {ac_number}.")
    return redirect(url_for("view_books"))


@app.route("/view_user/<usn>")
def view_user(usn):
    user = User.query.filter_by(username=usn).first()
    if user:
        borrowed_books = TransactionLog.query.filter_by(user=user).all()
        return render_template(
            "view_user.html",
            user=user,
            e=borrowed_books,
            title=f"View details for {user.username}",
        )
    flash(f"Could not find a user with USN = {usn}.")
    return redirect(url_for("view_all_users"))


@app.route("/populate_shelf_rack_numbers")
def pop_():
    entities = Entity.query.all()
    for entity in entities:
        entity.shelf_number = randint(1, 25)
        entity.rack_number = randint(1, 4)

        db.session.commit()

    return redirect(url_for("home"))


book_ids = [11075, 14646, 14647, 13372, 12894, 12893]
users = [6, 7, 8, 10, 11, 12, 2]


@app.route("/populate_borrowed_books")
def pop_books():
    for _ in book_ids:
        user = User.query.filter_by(id=choice(users)).first()
        b = Entity.query.filter_by(accession_number="4000").first()

        t = TransactionLog(user=user, entity=b)
        db.session.add(t)
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/populate_overdue_books")
def over():
    with app.app_context():
        entity = Entity.query.filter_by(id=20, is_borrowed=False).first()
        u = User.query.filter_by().first()
        entity.user = u
        entity.is_borrowed = True
        entity.borrowed_date = datetime.now()
        early_date = datetime.now() - timedelta(days=10)
        entity.due_date = early_date

        t = TransactionLog(user=u, entity=entity, due_date=early_date)
        db.session.add(t)
        db.session.commit()

    return redirect(url_for("view_books"))


@app.route("/fine_received", methods=["GET", "POST"])
@login_required
def fine_received():
    form = FineReceivedForm()

    if request.method == "GET":
        usn = request.args.get("usn")

        if usn is not None:
            form.payer.data = usn

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.payer.data).first()
        fine = FinesLog.query.filter_by(is_paid=False, user=user).first()

        if fine.amount_currently_due == int(form.amount.data):
            fine.is_paid = True
            fine.amount_currently_due = 0
            flash(f"Fine paid by {user.name} marked as paid.")

        elif fine.amount_currently_due < int(form.amount.data):
            fine.is_paid = True
            fine.amount_currently_due = 0
            flash("Excess amount paid")

        elif fine.amount_currently_due > int(form.amount.data):
            flash(
                f"{fine.amount_currently_due - form.amount.data} Rs outstanding payment left. Payment marked as partially done"
            )
            fine.amount_currently_due = fine.amount_currently_due - int(
                form.amount.data
            )

        db.session.commit()
        return redirect(url_for("view_fine_log"))
    return render_template("got_fine.html", form=form, title="Fine Slip")


@app.route("/add_holiday", methods=["GET", "POST"])
@login_required
def add_holiday():
    form = AddHolidayForm()
    if form.validate_on_submit():
        h = Holidays.query.filter_by(holiday=form.date.data).first()
        if (
            h is None
        ):  # TODO this doesnt work, duplicate holidays can be added - fix that
            holiday = Holidays(holiday=form.date.data)
            db.session.add(holiday)
            db.session.commit()
            flash(f"Holiday added for date {form.date.data}")
        else:
            flash(f"{form.date.data} is already a holiday ")
        return redirect(url_for("home"))
    return render_template("add_holiday.html", form=form)


@app.route("/suggest_a_book", methods=["GET", "POST"])
def suggest_a_book():
    form = SuggestBookForm()

    if form.validate_on_submit():
        u = User.query.filter_by(username=form.usn.data).first()
        if u is None:
            form.usn.errors.append("That USN does not exist.")
            return render_template(
                "suggest_book.html", form=form, title="Request a Book"
            )

        suggestion = Suggestions(
            user=u,
            book_name=form.book.data,
            author_name=form.author.data,
            submit_reason=form.reason.data,
        )

        db.session.add(suggestion)
        db.session.commit()

        flash("Book has been suggested successfully.")
        return redirect(url_for("catalog"))

    return render_template("suggest_book.html", form=form, title="Request a Book")


@app.route("/view_suggestions")
def view_suggestions():
    suggestions = Suggestions.query.all()
    return render_template(
        "suggestions.html", title="View Book Requests", suggestions=suggestions
    )


@app.route("/test_email")
def test_email():
    msg = Message(
        "Hello",
        sender="severusvirtanen@gmail.com",
    )

    msg.html = "<h1> <em> this works </em> </h1>"

    mail.send(msg)

    flash("Message sent successfully.")
    return redirect(url_for("home"))
