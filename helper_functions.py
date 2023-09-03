from datetime import timedelta


def find_dif(datetime1, datetime2):
    if datetime2 is None:
        return False
    if datetime1.date() > datetime2.date():
        time_dif = datetime1 - datetime2
        return time_dif.days
    else:
        return False
