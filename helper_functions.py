from datetime import timedelta


def exceeds_seven_days(datetime1, datetime2):
    time_difference = abs(datetime1 - datetime2)

    # Check if the time difference exceeds 7 days
    if time_difference > timedelta(days=7):
        return True
    else:
        return False
