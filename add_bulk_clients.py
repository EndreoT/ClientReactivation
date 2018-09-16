"""
Allows the user to convert line separated client information from the bulk client staging text file to the
json database only if it is correctly formatted.
Note: If an email is included, then a reminder date must be included as well.
"""

import os
from typing import List, Dict

from custom_exceptions import DateTooFarInPast, IncorrectNumberOfTerms, InvalidEmail
from manage_datetime import datetime_to_string, default_rem_date, prepare_date
from manage_db import add_to_db
from manage_email import validate_email

infile = os.path.join(os.path.dirname(__file__), 'bulk_client_staging.txt')


def add_bulk_clients_to_db(file, outfile="db.json") -> (List[str], Dict[str, List[str]]):
    """
    Adds correctly formatted line separated client information from the bulk client staging text file to the database.
    Otherwise, returns a dictionary showing which client information needs fixing.
    """

    with open(file, "r") as rf:
        client_list = rf.readlines()
        correctly_formatted_clients = []
        incorrectly_formatted_clients = {"Incorrect number of terms": [],
                                         "Bad date": [],
                                         "Incorrect date formatting": [],
                                         "Date too far in past": [],
                                         "Email does not contain '@' sign": []
                                         }
        for client in client_list:
            if client == "\n":
                continue
            client_info = client.strip().split()
            try:
                if len(client_info) < 3 or len(client_info) > 5:
                    raise IncorrectNumberOfTerms
                first_name, last_name = client_info[0], client_info[1]
                last_visit = prepare_date(client_info[2], future=True)
                if len(client_info) > 3:
                    rem_date = prepare_date(client_info[3])
                else:
                    rem_date = datetime_to_string(default_rem_date)
                if len(client_info) > 4:
                    email = client_info[4]
                    if not validate_email(email):
                        raise InvalidEmail
                else:
                    email = None
            except IncorrectNumberOfTerms:
                incorrectly_formatted_clients["Incorrect number of terms"].append(client.strip())
            except ValueError:
                incorrectly_formatted_clients["Bad date"].append(client.strip())
            except AttributeError:
                incorrectly_formatted_clients["Incorrect date formatting"].append(client.strip())
            except DateTooFarInPast:
                incorrectly_formatted_clients["Date too far in past"].append(client.strip())
            except InvalidEmail:
                incorrectly_formatted_clients["Email does not contain '@' sign"].append(client.strip())
            else:
                correctly_formatted_clients.append(str(client_info[0]) + " " + str(client_info[1]))
                add_to_db(first_name, last_name, last_visit, rem_date, email, file=outfile)

        # Remove correctly formatted clients in bulk client staging
        with open(file, "w") as wf:
            wf.truncate()
            wf.seek(0)
            for issue in incorrectly_formatted_clients.values():
                for client in issue:
                    try:
                        wf.write(client + "\n")
                    except TypeError:
                        continue

    return correctly_formatted_clients, incorrectly_formatted_clients


def main():
    correctly_formatted_clients, incorrectly_formatted_clients = add_bulk_clients_to_db(infile)
    print("successfully wrote to file {}.".format(correctly_formatted_clients))
    print("\nEach client has at least one incorrectly formatted term in the following areas. "
          "User must fix the following manually:")
    for key, value in incorrectly_formatted_clients.items():
        print(key, value)


if __name__ == "__main__":
    main()
