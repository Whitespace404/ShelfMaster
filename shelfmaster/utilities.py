from datetime import datetime, timedelta
from functools import wraps

import openpyxl
from flask import flash, redirect, url_for
from flask_login import current_user

from shelfmaster import db, app
from shelfmaster.models import TransactionLog, Admin, User, Entity


def super_admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role_id < 2:
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("admin_login"))
        return func(*args, **kwargs)

    return decorated_view


HOLIDAYS = [datetime(2023, 9, 18)]


def is_weekend(day):
    return day.weekday() >= 5


def business_days_count(start_date, end_date, holidays):
    days_count = 0
    current_date = start_date

    while current_date <= end_date:
        if not is_weekend(current_date) and current_date not in holidays:
            days_count += 1
        current_date += timedelta(days=1)

    return days_count


def find_bus_days(datetime1, datetime2):
    bdays = business_days_count(datetime1, datetime2, HOLIDAYS)
    return bdays


def find_dif(datetime1, datetime2):
    if datetime2 is None:
        return False
    if datetime1.date() > datetime2.date():
        time_dif = datetime1 - datetime2
        return time_dif.days
    else:
        return False


def borrow_book(user, entity):
    """This function can be used to borrow a book. Takes two inputs,
    a user object and a book object."""

    entity.user = user
    entity.is_borrowed = True
    entity.borrowed_date = datetime.now()
    entity.due_date = datetime.now() + timedelta(7)

    log = TransactionLog(user=user, entity=entity)
    db.session.add(entity)
    db.session.add(log)
    db.session.commit()


def create_database():
    with app.app_context():
        db.create_all()

        admin = Admin(username="rahulreji", password="power", role_id=2)
        db.session.add(admin)
        db.session.commit()

        for usn_name in read_namelist():
            u = User(
                username=usn_name[0],
                name=usn_name[1],
                is_teacher=False,
                class_section="4A",
            )
            db.session.add(u)
            db.session.commit()

        for book_details in read_booklist():
            entity = Entity(
                type="Book",
                title=book_details["title"],
                author=book_details["author"],
                accession_number=book_details["accession_number"],
                call_number=book_details["call_number"],
                publisher=book_details["publisher"],
                place_of_publication=book_details["place_of_publication"],
                isbn=book_details["isbn"],
                vendor=book_details["vendor"],
                bill_number=book_details["bill_number"],
                amount=book_details["price"],
                language="English",
            )
            db.session.add(entity)
            db.session.commit()


def convert_name(name):
    try:
        parts = name.split(", ")
    except AttributeError:
        return name

    if len(parts) == 2:
        last_name, first_name = parts
        converted_name = f"{first_name} {last_name}"
        return converted_name
    else:
        return name


def read_booklist():
    wb = openpyxl.load_workbook("master.xlsx")
    sheet = wb["Accession Details"]

    result_dict = []
    for row in sheet.iter_rows(min_row=3, values_only=True):
        details = dict()
        details["accession_number"] = row[0]
        name = row[3]
        details["author"] = convert_name(name)
        details["title"] = convert_name(row[4])
        details["call_number"] = row[5]
        details["publisher"] = row[6]
        details["place_of_publication"] = row[7]
        details["isbn"] = row[8]
        details["vendor"] = row[9]
        details["bill_number"] = row[10]
        details["price"] = row[12]
        result_dict.append(details)

    return result_dict


def read_namelist():
    wb = openpyxl.load_workbook("master.xlsx")
    sheet = wb["Issue Details"]

    result_list = []
    for row in sheet.iter_rows(min_row=3, values_only=True):
        result_list.append((row[1], row[2]))

    return result_list
