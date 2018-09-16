"""Provides helper functions to add to, search, update, and delete the contents of the database."""

import re

from tinydb import TinyDB, Query
from tinydb.operations import add, set as set_val

from manage_datetime import datetime_to_string, is_rem_date_in_past, validate_date


def add_to_db(first_name: str, last_name: str,
              last_visit: str,
              reminder_date: str,
              email=None,
              times_contacted=0,
              file='db.json'
              ) -> None:
    """Adds a client information to the json database."""

    with TinyDB(file) as db:
        db.insert({"first name": first_name,
                   "last name": last_name,
                   "last visit": last_visit,
                   "rem date": reminder_date,
                   "email": email,
                   "times contacted": times_contacted
                   })


def get_client(first_name: str, last_name: str, file="db.json") -> list:
    """Returns a list containing client information from the database that matches the client's first and last name."""

    with TinyDB(file) as db:
        query = Query()
        result = db.search(
            (query["first name"].matches(first_name, flags=re.IGNORECASE))
            & (query["last name"].matches(last_name, flags=re.IGNORECASE))
        )
    return result


def delete_client(first_name: str, last_name: str, file="db.json") -> None:
    """Deletes all clients from the database which match the client's first and last name."""

    with TinyDB(file) as db:
        query = Query()
        db.remove(
            (query["first name"].matches(first_name, flags=re.IGNORECASE))
            & (query["last name"].matches(last_name, flags=re.IGNORECASE))
        )


def update_times_contacted(first_name: str, last_name: str, addition: int = 1, file="db.json") -> None:
    """Increments the 'times contacted' field in the database for all clients that match the first and last name."""

    with TinyDB(file) as db:
        query = Query()
        db.update(add("times contacted", addition), (query["first name"].matches(first_name, flags=re.IGNORECASE))
                  & (query["last name"].matches(last_name, flags=re.IGNORECASE))
                  )


def get_times_contacted(first_name: str, last_name: str, file="db.json") -> int:
    """Returns the times a client has been contacted for clients that match the first and last name."""

    with TinyDB(file) as db:
        query = Query()
        result = db.search((query["first name"].matches(first_name, flags=re.IGNORECASE))
                           & (query["last name"].matches(last_name, flags=re.IGNORECASE))
                           )
    try:
        return result[0]["times contacted"]
    except IndexError:
        return -1


def update_clients_with_rem_date_in_past(file="db.json") -> None:
    """Increments the 'times contacted' field for all clients with reminder dates in the past."""

    with TinyDB(file) as db:
        query = Query()
        db.update(add("times contacted", 1), query["rem date"].test(is_rem_date_in_past))


def update_rem_date(first_name: str, last_name: str, date: str, file="db.json") -> None:
    """Verifies and sets the reminder date for a client matching the first and last name."""

    try:
        date = datetime_to_string(validate_date(date))
        with TinyDB(file) as db:
            query = Query()
            db.update(set_val("rem date", date), (query["first name"].matches(first_name, flags=re.IGNORECASE))
                      & (query["last name"].matches(last_name, flags=re.IGNORECASE))
                      )
    except AttributeError:
        print("Date is not correctly formatted")


def get_all_db_contents(file="db.json") -> list:
    """Returns all clients from the database."""

    with TinyDB(file) as db:
        return db.all()


def delete_db_contents(file="db.json") -> None:
    """Deletes all clients from the database."""
    with TinyDB(file) as db:
        db.purge()


def set_rem_date_for_all(date) -> None:
    """Validates and sets the reminder date for all clients. Helpful for testing purposes."""

    try:
        date = datetime_to_string(validate_date(date))
        with TinyDB("db.json") as db:
            db.update({"rem date": date})
    except ValueError:
        print("Date is not correctly formatted")
