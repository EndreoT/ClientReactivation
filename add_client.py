"""Allows the user to add clients one at a time to the database using the command line."""

import argparse
import sys
from typing import List, Union

from custom_exceptions import DateTooFarInPast, InvalidEmail
from manage_datetime import datetime_to_string, default_rem_date, prepare_date
from manage_db import add_to_db
from manage_email import validate_email


def get_args(args: List[str]) -> argparse.Namespace:
    """Gets client information through the command line."""

    parser = argparse.ArgumentParser()
    parser.add_argument("first_name", type=str, help="Client's first name.")
    parser.add_argument("last_name", type=str, help="Client's last name.")
    parser.add_argument("last_visit", type=str, help="Date of their last visit in the form mm/dd/yyyy or mm-dd-yyyy")
    parser.add_argument("--rem_date", type=str,
                        default=datetime_to_string(default_rem_date),
                        help="Optionally choose a custom reminder date."
                        )
    parser.add_argument("--email", type=str, default=None, help="Optional client email to be used for reminders.")
    return parser.parse_args(args)


def write_to_db(args: argparse.Namespace, db="db.json") -> Union[List[str], None]:
    """Writes client information to json database if it is correctly formatted."""

    first_name, last_name, email = args.first_name, args.last_name, args.email
    try:
        last_visit = prepare_date(args.last_visit, future=True)
        reminder_date = prepare_date(args.rem_date, past=True)
        if not validate_email(email):
            raise InvalidEmail
    except AssertionError:
        print("Incorrect formatting. Input requires 3 elements: first name, last name, date_of_last_visit")
    except ValueError:
        print("Date of last visit is in the future, reminder date is in the past, "
              "or date is impossible. Please try again")
    except AttributeError:
        print("Incorrect date formatting. Please use date format mm/dd/yyyy or mm-dd-yyyy and try again")
    except DateTooFarInPast:
        print("Date is too far in the past.")
    except InvalidEmail:
        print("Email does not contain '@' sign.")
    else:
        print("Wrote to file - {} {}, Client's last visit: {}, Client to be reminded on {}, Client's email: {}"
              .format(first_name, last_name, last_visit, reminder_date, email))
        add_to_db(first_name, last_name, last_visit, reminder_date, email, file=db)
        return [first_name, last_name, last_visit, reminder_date, email]
    return None


def main():
    args = get_args(sys.argv[1:])
    write_to_db(args)


if __name__ == "__main__":
    main()
