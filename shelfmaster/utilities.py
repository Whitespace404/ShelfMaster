from datetime import datetime, timedelta
from functools import wraps

import openpyxl
from flask import flash, redirect, url_for
from flask_login import current_user

from shelfmaster import db, app
from shelfmaster.models import TransactionLog, Admin, User, Entity, Holidays


def super_admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role_id < 2:
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("admin_login"))
        return func(*args, **kwargs)

    return decorated_view


"""
is_overdue(datetime2, datetime1)

return number of days book is overdue by
if its not overdue return None
"""
def is_weekend(day):
    return day.weekday() >= 5


def business_days_count(start_date, end_date, holidays):
    if start_date == end_date:
        return None
    days_count = 0
    current_date = start_date

    while current_date < end_date:
        if not is_weekend(current_date) and (current_date not in holidays):
            days_count += 1
        current_date += timedelta(days=1)

    return days_count


def find_bus_days(datetime1, datetime2):
    HOLIDAYS = query_holidays()
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


def calculate_overdue_days(returned_date, deadline):
    if returned_date.date() <= deadline.date():
        return None
    else:
        bus_days_overdue = find_bus_days(deadline, returned_date)
        if bus_days_overdue == 1:
            return None
        else:
            return bus_days_overdue


def borrow_book(user, entity):
    """This function can be used to borrow a book. Takes two inputs,
    a user object and a book object."""

    entity.user = user
    entity.is_borrowed = True
    entity.borrowed_date = datetime.now()
    entity.due_date = calculate_return_date(datetime.now().date())

    log = TransactionLog(user=user, entity=entity)
    db.session.add(entity)
    db.session.add(log)
    db.session.commit()


def create_database():
    with app.app_context():
        db.create_all()

        admin = Admin(username="admin", password="power", role_id=2)
        db.session.add(admin)
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


def time_ago(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    Modified from: http://stackoverflow.com/a/1551394/141084
    """
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    else:
        raise ValueError("invalid date %s of type %s" % (time, type(time)))
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ""

    if day_diff == 0:
        if second_diff < 10:
            return "Just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff / 365) + " years ago"


def calculate_return_date(borrow_date):
    holidays_list = query_holidays()

    d_date = borrow_date + timedelta(7)
    while (not is_weekend(d_date)) and (datetime.now().date() not in holidays_list) and d_date > datetime.now().date(): # error handle here
        d_date = d_date - timedelta(1)
    
    return d_date

def query_holidays():
    holidays_list = []
    with app.app_context():
        hols = Holidays.query.all()
        for hol in hols:
            if hol.holiday not in holidays_list:
                holidays_list.append(hol.holiday)
        return holidays_list
