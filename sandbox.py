from shelfmaster import db, app
from shelfmaster.models import Holidays
from datetime import timedelta, datetime


def is_weekend(day):
    return day.weekday() >= 5


def find_bus_days(datetime1, datetime2):
    HOLIDAYS = query_holidays()
    bdays = business_days_count(datetime1, datetime2, HOLIDAYS)
    return bdays


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


def calculate_overdue_days(returned_date, deadline):
    if returned_date.date() <= deadline.date():
        return None
    else:
        bus_days_overdue = find_bus_days(deadline, returned_date)
        return (bus_days_overdue - 1)


def query_holidays():
    holidays_list = []
    with app.app_context():
        hols = Holidays.query.all()
        for hol in hols:
            if hol.holiday not in holidays_list:
                holidays_list.append(hol.holiday)
        return holidays_list

def main():
    print(
        str(calculate_overdue_days(datetime(2024, 11, 12, 0, 0), datetime(2024, 11, 5, 0, 0)) * 10) + " Rs"
    )

main()
