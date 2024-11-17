from shelfmaster import db, app
from shelfmaster.models import Holidays


def query_holidays():
    with app.app_context():
        h = Holidays.query.all()
        for hol in h:
            print(hol)
            print(type(hol))


query_holidays()
