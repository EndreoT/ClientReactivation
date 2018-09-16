"""Includes helper functions to validate datetime objects and to convert between string and datetime objects."""

import datetime
import re
from typing import List

from custom_exceptions import DateTooFarInPast

date_too_far_in_past = 11

reactivation_time_period = 30
default_rem_date = datetime.datetime.now() + datetime.timedelta(reactivation_time_period)


def datetime_to_string(date: datetime.datetime) -> str:
    """
    Converts a datetime object to a string.

    >>> datetime_to_string(datetime.datetime(2018, 3, 4))
    '3/4/2018'
    """
    return str(date.month) + "/" + str(date.day) + "/" + str(date.year)


def separated_date_to_datetime(date: List[str]) -> datetime.datetime:
    """
    Converts a date in list format as [year, month, day] to a datetime object.

    >>> separated_date_to_datetime(["2017", "3", "15"])
    datetime.datetime(2017, 3, 15, 0, 0)
    """
    return validate_date(date[1] + "/" + date[2] + "/" + date[0])


def string_to_datetime(date: str) -> datetime.datetime:
    return validate_date(date)


def date_is_in_future(date: datetime.datetime) -> bool:
    return datetime.datetime.now().date() < date.date()


def date_is_in_past(date: datetime.datetime) -> bool:
    return datetime.datetime.now().date() > date.date()


def is_rem_date_in_past(date: str) -> bool:
    return date_is_in_past(string_to_datetime(date))


def date_is_today(date: datetime.datetime) -> bool:
    return datetime.datetime.now().date() == date.date()


def prepare_date(date: str, future=False, past=False) -> str:
    """
    Validates a date, raises an exception if it is not expected to be in the future or past, then returns a
    string representation of the date.
    """
    ret_date = validate_date(date)
    if future:
        if date_is_in_future(ret_date):
            raise ValueError
    elif past:
        if date_is_in_past(ret_date):
            raise ValueError
    return datetime_to_string(ret_date)


def validate_date(date: str) -> datetime.datetime:
    """
    Validates a date in mm/dd/yyyy string format and returns a datetime object.

    >>> validate_date("3/15/2017")
    datetime.datetime(2017, 3, 15, 0, 0)
    """

    match = re.compile(r"^(\d|\d{2})[/-](\d|\d{2})[/-](\d{2}|\d{4})$")
    regex = re.match(match, date)

    month, day, year = regex.group(1), regex.group(2), regex.group(3)
    if len(year) == 2:  # Convert two digit date to four digit date
        year = str(datetime.datetime.now().year)[:2] + year
    check_date = datetime.datetime(*(int(i) for i in (year, month, day)))
    # Check if date is too old
    if datetime.datetime.now() - datetime.timedelta(weeks=52 * date_too_far_in_past) > check_date:
        raise DateTooFarInPast
    return check_date
