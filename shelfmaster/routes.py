from datetime import datetime, timedelta, date
from random import randint, choice
import os

from flask import render_template, redirect, request, flash, url_for, abort, Markup
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, desc
from werkzeug.utils import secure_filename


from shelfmaster import db, app
from shelfmaster.forms import (
    LoginForm,
    BorrowForm,
    ReturnForm,
    ConfirmReturnForm,
    SuggestBookForm,
    ReportDamageForm,
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
    ReturnLog,
)
from shelfmaster.utilities import (
    super_admin_required,
    find_dif,
    borrow_book,
    create_database,
    calculate_overdue_days,
    time_ago,
)
from shelfmaster.utilities_master import (
    read_namelist_from_upload,
    read_booklist_from_upload,
)
from shelfmaster.const import ROLE_PERMS


@app.route("/")
def home():
    if current_user.is_authenticated:
        books = Entity.query.filter_by().count()
        transactions = TransactionLog.query.count()
        users = User.query.count()
        borrowers = Entity.query.filter_by(is_borrowed=True).count()
        tlog = TransactionLog.query.order_by(TransactionLog.id.desc()).limit(6).all()
        rlog = ReturnLog.query.order_by(ReturnLog.id.desc()).limit(6).all()
        today = datetime.combine(date.today(), datetime.max.time())
        pending_returns_count = (
            User.query.join(Entity, User.borrowed_entities)
            .filter(Entity.is_borrowed == True, Entity.due_date <= today)
            .count()
        )
        return render_template(
            "admin_tools.html",
            title="Admin Tools",
            books=books,
            transactions=transactions,
            users=users,
            borrowers=borrowers,
            tlog=tlog,
            rlog=rlog,
            time_ago=time_ago,
            pending_returns_count=pending_returns_count,
        )
    year = date.today().year
    return render_template("home.html", title="Home", year=year)


@app.route("/borrow/", methods=["GET", "POST"])
def borrow():
    form = BorrowForm()

    if request.method == "GET":
        accession_number = request.args.get("accession_number", type=int)
        usn = request.args.get("usn")

        if accession_number is not None:
            form.book_id.data = accession_number
        if usn is not None:
            form.usn.data = usn

    if form.validate_on_submit():
        u = User.query.filter_by(username=form.usn.data).first()
        entity = Entity.query.filter_by(accession_number=form.book_id.data).first()

        # age_category = entity.call_number.split("/")[0]

        # ROLE_PERMS.index(age_category)

        # Now find the ROLE PERM of the user using the database
        # and then compare if it is equal or lesser than the
        # previous user and then compile the results

        if u is None:
            form.usn.errors.append("USN does not exist")
            return render_template("borrow.html", form=form, title="Borrow A Book")
        if entity is None:
            form.book_id.errors.append("That book doesn't exist in the database yet.")
            return render_template("borrow.html", form=form, title="Borrow A Book")
        if entity.is_borrowed:
            if entity.user.username == form.usn.data:
                # TODO test this: renewing book
                entity.due_date = datetime.now() + timedelta(days=7)
                db.session.commit()
                flash(f"Return date extended to {entity.due_date.strftime('%d/%m/%y')}")
                return redirect(url_for("home"))
            else:
                form.book_id.errors.append(
                    f"{form.book_id.data} borrowed by {entity.user.name}."
                )
            return render_template("borrow.html", form=form, title="Borrow A Book")
        if u.is_teacher:
            borrow_book(u, entity)
            flash(f"Book borrowed successfully.")
            return redirect(url_for("borrow"))
        elif len(u.borrowed_entities) == 0:
            # if entity.call_number
            borrow_book(u, entity)
            flash(
                f"Book borrowed successfully. Please return it before {entity.due_date.strftime('%d/%m/%y')}"
            )
            return redirect(url_for("borrow"))
        else:
            flash(Markup(f"Book {u.borrowed_entities[0]} is still pending for return. "))
    users = User.query.all()
    return render_template("borrow.html", form=form, title="Borrow A Book", users=users)


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


@app.route("/confirm_return/<int:accession_number>", methods=["GET", "POST"])
def confirm_return(accession_number):
    form = ConfirmReturnForm()
    b = Entity.query.filter_by(accession_number=accession_number).first()
    if not b.due_date:
        return "error book was not borrowed"
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

        return_ = ReturnLog(
            user=b.user,
            entity=b,
            returned_time=current_dt,
            librarian_remarks=form.librarian_remarks.data,
        )
        db.session.add(return_)

        if form.librarian_remarks.data:
            cdate = datetime.now().date()
            b.remarks = "\n" + str(cdate) + " | " + form.remarks.data

        b.is_borrowed = False
        b.user = None
        b.due_date = None
        b.borrowed_date = None

        db.session.commit()

        flash("Book was returned successfully.")
        return redirect(url_for("return_"))

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


@app.route("/view_all_users", methods=["GET", "POST"])
@login_required
def view_all_users():
    if request.method == "POST":
        return redirect(url_for("view_all_users", clas=request.form["clas"]))
    page = request.args.get("page", default=1, type=int)
    class_section = request.args.get("clas")
    # TODO redo this logic

    if not class_section:
        if request.args.get("borrowed_only"):
            logs = User.query.filter(User.borrowed_entities != None).paginate(
                page=page, per_page=40
            )
        else:
            logs = User.query.paginate(page=page, per_page=40)
    else:
        if request.args.get("borrowed_only"):
            logs = User.query.filter(User.borrowed_entities != None).paginate(
                page=page, per_page=40
            )
        else:
            logs = User.query.filter_by(class_section=class_section).paginate(
                page=page, per_page=40
            )
    classes = db.session.query(User.class_section).distinct().all()
    title = f"| {class_section}" if class_section else None
    return render_template(
        "view_users.html",
        logs=logs,
        title=title,
        classes=classes,
        class_section=class_section,
    )


@app.route("/view_admin_log")
@super_admin_required
def view_admin_log():
    logs = AdminActionsLog.query.filter_by().order_by(desc(AdminActionsLog.id))
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
    page = request.args.get("page", default=1, type=int)
    borrowed_only = request.args.get("borrowed_only")
    if not borrowed_only:
        books = Entity.query.filter(Entity.remarks == None).paginate(
            page=page, per_page=40
        )
    else:
        books = Entity.query.filter(Entity.is_borrowed == True).paginate(
            page=page, per_page=40
        )
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


@app.route("/view_daily_transactions")
@login_required
def view_daily_transactions():
    today = datetime.now().date()

    transactions = TransactionLog.query.filter(
        func.date(TransactionLog.borrowed_time) == today
    ).all()

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


@app.route("/add_entity", methods=["GET", "POST"])
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
            isbn=form.isbn.data,
            vendor=form.vendor.data,
            bill_number=form.bill_number.data,
            bill_date=form.bill_date.data,
            amount=form.amount.data,
            remarks=form.remarks.data,
            language=form.language.data,
        )
        db.session.add(e)
        db.session.commit()

        log_message = f"Added a book with Accession Number:{form.accession_number.data}"
        action = AdminActionsLog(username=current_user.username, action=log_message)
        db.session.add(action)
        db.session.commit()

        flash(f"Book added successfully")
        return redirect(url_for("add_entity"))
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
        elif form.report_type.data == "fines":
            return redirect(url_for("view_fine_log"))
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
    page = request.args.get("page", default=1, type=int)
    if form.validate_on_submit():
        if form.criteria.data in SEARCH_TYPE_MAPPING:
            search_attribute = SEARCH_TYPE_MAPPING[form.criteria.data]
            q = Entity.query.filter(
                search_attribute.ilike(f"%{form.query.data}%")
            ).paginate(page=page, per_page=40)
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


@app.route("/populate_overdue_books")
def over():
    with app.app_context():
        entity = Entity.query.filter_by(id=20, is_borrowed=False).first()
        u = User.query.filter_by().first()
        entity.user = u
        entity.is_borrowed = True
        entity.borrowed_date = datetime.now() - timedelta(days=8)
        early_date = datetime.now() - timedelta(days=1)
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
        if (h is None):
            # TODO this doesnt work, duplicate holidays can be added - fix that
            holiday = Holidays(holiday=form.date.data)
            db.session.add(holiday)
            db.session.commit()
            flash(f"Holiday added for date {form.date.data}")
        else:
            flash(f"{form.date.data} is already a holiday ")
        return redirect(url_for("add_holiday"))
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
@login_required
def view_suggestions():
    suggestions = Suggestions.query.all()
    return render_template(
        "suggestions.html", title="View Book Requests", suggestions=suggestions
    )


@app.route("/view_defaulters")
@login_required
def view_defaulters():
    today = datetime.combine(date.today(), datetime.max.time())
    logs = User.query.join(Entity, User.borrowed_entities).filter(
        Entity.is_borrowed == True, Entity.due_date <= today
    ).order_by(User.class_section, User.name)
    return render_template("view_defaulters.html", logs=logs, title="Pending Returns")


@app.route("/privacy_policy")
def privacy_policy():
    return render_template("privacy_policy.html", title="Privacy Policy")


@app.route("/report_damage", methods=["GET", "POST"])
@login_required
def report_damage():
    form = ReportDamageForm()
    if request.method == "GET":
        acc_no = request.args.get("accession_number")
        if acc_no:
            form.book_id.data = acc_no
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.usn.data).first()
        book = Entity.query.filter_by(accession_number=form.book_id.data).first()

        current_dt = datetime.now().date()
        book.remarks += f"\n {str(current_dt)} | {form.remarks.data}"

        fine = FinesLog(
            user=user,
            entity=book,
            fine_amount=form.fine_amt.data,
            amount_currently_due=form.fine_amt.data,
        )
        db.session.add(fine)
        db.session.commit()

        return redirect(url_for("view_fine_log"))
    return render_template("report_damage.html", form=form)


@app.route("/delete_class")
@login_required
def delete_class():
    class_ = request.args.get("class")
    users = User.query.filter_by(class_section=class_).all()

    for user in users:
        db.session.delete(user)
    db.session.commit()

    flash(f"Deleted class {class_}")
    return redirect(url_for("view_all_users"))


@app.route("/upload_namelist")
@login_required
def upload_namelist():
    return render_template("upload_student_details.html")


@app.route("/upload_namelist", methods=["POST"])
@login_required
def name_upload():
    uploaded_file = request.files["file"]
    filename = uploaded_file.filename
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
        abort(400)
    if filename != "":
        filepath = os.path.join(
            app.root_path,
            app.config["UPLOAD_PATH"],
            secure_filename(filename),
        )
        uploaded_file.save(filepath)

        results = read_namelist_from_upload(filepath)
        for result in results:
            user = User.query.filter_by(username=result["usn"]).first()
            if not user:
                u = User(
                    class_section=result["class_section"],
                    username=result["usn"],
                    name=result["name"],
                    rollno=result["roll_number"],
                    is_teacher=False,
                )
                db.session.add(u)
            else:
                user.class_section = result["class_section"]
                user.username = result["usn"]
                user.name = result["name"]
                db.session.add(user)
            db.session.commit()
        flash("Added to database successfully.")
        return redirect(url_for("view_all_users"))
    return redirect(url_for("upload_namelist"))


@app.route("/edit_user/<usn>/", methods=["GET", "POST"])
@login_required
def edit_user(usn):
    user = User.query.filter_by(username=usn).first()
    form = AddUserForm()

    if form.validate_on_submit():
        if form.username.data != usn:
            assert User.query.filter_by(username=form.username.data).first() is None
            user.username = (
                form.username.data
            )  # TODO raise form error here if USN is not unique
        user.name = form.name.data
        user.is_teacher = True if form.is_teacher.data == "Teacher" else False
        user.class_section = form.class_section.data

        db.session.add(user)
        db.session.commit()

        flash("User details updated.")
        return redirect(url_for("view_all_users"))

    form.username.data = user.username
    form.name.data = user.name
    form.is_teacher.data = user.is_teacher
    form.class_section.data = user.class_section

    return render_template("edit_user.html", form=form)


@login_required
@app.route("/delete_user/<usn>")
def delete_user(usn):
    user = User.query.filter_by(username=usn).first()
    db.session.delete(user)
    db.session.commit()
    flash(f"{user.username} - {user.name} deleted from database successfully")
    return redirect(url_for("view_all_users"))


@app.route("/edit_book/<accession_number>", methods=["GET", "POST"])
@login_required
def edit_book(accession_number):
    form = AddBookForm()
    entity = Entity.query.filter_by(accession_number=accession_number).first()
    if form.validate_on_submit():
        if form.accession_number.data != accession_number:
            assert (
                Entity.query.filter_by(
                    accession_number=form.accession_number.data
                ).first()
                is None
            )
            entity.accession_number = form.accession_number.data
            # TODO raise form error here if USN is not unique

        entity.title = form.title.data
        entity.author = form.author.data
        entity.accession_number = form.accession_number.data
        entity.call_number = form.call_number.data
        entity.publisher = form.publisher.data
        entity.isbn = form.isbn.data
        entity.vendor = form.vendor.data
        entity.bill_number = form.bill_number.data
        entity.bill_date = form.bill_date.data
        entity.price = form.amount.data
        entity.remarks = form.remarks.data
        entity.language = form.language.data

        db.session.add(entity)
        db.session.commit()

        flash("Book details updated.")
        return redirect(url_for("view_entity", ac_number=entity.accession_number))

    form.title.data = entity.title
    form.author.data = entity.author
    form.accession_number.data = entity.accession_number
    form.call_number.data = entity.call_number
    form.publisher.data = entity.publisher
    form.isbn.data = entity.isbn
    form.vendor.data = entity.vendor
    form.bill_number.data = entity.bill_number
    form.bill_date.data = entity.bill_date
    form.amount.data = entity.price
    form.remarks.data = entity.remarks
    form.language.data = entity.language

    return render_template("edit_book.html", form=form)


@app.route("/upload_booklist")
@login_required
def upload_booklist():
    return render_template("upload_book_details.html")


@app.route("/upload_booklist", methods=["POST"])
@login_required
def book_upload():
    uploaded_file = request.files["file"]
    filename = uploaded_file.filename
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
        abort(400)
    if filename != "":
        filepath = os.path.join(
            app.root_path,
            app.config["UPLOAD_PATH"],
            secure_filename(filename),
        )
        uploaded_file.save(filepath)

        results = read_booklist_from_upload(filepath)
        for result in results:
            book = Entity.query.filter_by(
                accession_number=result["accession_number"]
            ).first()

            entity = Entity(
                type="Book",
                accession_number=result["accession_number"],
                author=result["author"],
                title=result["title"],
                call_number=result["call_number"],
                publisher=result["publisher"],
                isbn=result["isbn"],
                vendor=result["vendor"],
                bill_number=result["bill_number"],
                bill_date=result["bill_date"],
                price=result["price"],
                remarks=result["remarks"],
                language=result["language"],
            )
            db.session.add(entity)
            db.session.commit()
        flash("Added to database successfully.")
        return redirect(url_for("view_books"))
    return redirect(url_for("upload_namelist"))
