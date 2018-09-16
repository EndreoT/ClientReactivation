"""
Creates a list of clients to be contacted who have not had an appointment since the given reactivation time period.
It is suggested to automatically run this program at regular intervals to catch clients who should be reactivated.
Client information is pulled from the json database.
"""

import tkinter as tk
from tkinter import messagebox
from typing import List

from tinydb import TinyDB, Query
from tinydb.operations import add, set as set_val

from client import Client
from manage_datetime import date_is_in_past, date_is_today, datetime_to_string, default_rem_date, string_to_datetime
from manage_db import add_to_db
from manage_email import send_email


# TODO automatically schedule this task using Python
# TODO distinguish between different clients with same name

remove_counter = 1


def get_clients_to_be_reactivated(file="db.json") -> List[Client]:
    """ Returns a list of clients who's reactivation date is today or in the past and should be contacted. """
    with TinyDB(file) as db:
        query = Query()
        result = db.search(query["rem date"].test(contact_now))
        output = []
        for client in result:
            output.append(Client(client["first name"], client["last name"],
                                 client["last visit"], client["rem date"],
                                 client["email"]
                                 ))
    return output


def contact_now(date: str) -> bool:
    """
    Returns true if date is today or in past, otherwise false.
    >>> contact_now("3/5/18")
    True
    """

    time_date = string_to_datetime(date)
    return date_is_today(time_date) or date_is_in_past(time_date)


def update_only_emailed_clients(recipient_list, file="db.json") -> None:
    """Increments the 'times contacted' field for only clients that were just email reminders. Also,
    sets the reminder date for these clients to the default reminder date."""

    with TinyDB(file) as db:
        for client in recipient_list:
            query = Query()
            db.update(add("times contacted", 1), (query["first name"].matches(client.get_first_name())
                                                  & (query["last name"].matches(client.get_last_name()))))
            db.update(set_val("rem date", datetime_to_string(default_rem_date)),
                      (query["first name"].matches(client.get_first_name())
                       & (query["last name"].matches(client.get_last_name())
                          )))


def remove_fully_contacted_clients(infile="db.json", outfile="fully_contacted_clients_db.json") -> None:
    """
    Removes clients from the database whose 'times contacted' field is greater than the number of times that
    they should be contacted (remove_counter). It then stores those clients in the fully contacted client database.
    """

    with TinyDB(infile) as db:
        query = Query()
        prev_contacted = db.search(query["times contacted"] > 1)
        for client in prev_contacted:
            add_to_db(client["first name"], client["last name"], client["last visit"],
                      client["rem date"], client["email"], times_contacted=client["times contacted"], file=outfile)
        db.remove(query["times contacted"] > remove_counter)


class View:
    """
    Creates a GUI showing which clients are ready to be contacted. If the client has an email address field,
    the user can send email reminders to those clients.
    """

    def __init__(self, client_list: List[Client]):
        self.master = tk.Tk()
        self.master.title("List of Clients to be Contacted")
        self.client_list = client_list
        self.int_var_list = []
        self.buttons = []
        self._make_scrollbar()
        self._make_labels()
        self.email_button = self._make_email_button()
        self._make_checkboxes()
        self.master.mainloop()

    def get_recipients(self) -> List[Client]:
        """Obtains all clients receiving email reminders."""

        index_list = [i for i in range(len(self.int_var_list)) if self.int_var_list[i].get() == 1]
        return [self.client_list[i] for i in index_list]

    def _make_email_button(self) -> tk.Button:
        button = tk.Button(self.interior, text='Send email', command=self._show_popup)
        button.pack(side="top", fill="both")
        return button

    def _show_popup(self) -> None:
        """Shows popup window confirming emails to be sent to the selected clients."""

        top = tk.Toplevel()
        email_list_len = len(self.get_recipients())
        msg = tk.messagebox.askquestion('Confirm send emails', 'Are you sure you want to email {} client{}?'
                                        .format(email_list_len, "s" if email_list_len > 1 else ""),
                                        icon='warning')
        if msg == "yes":
            self._disable_buttons()
            email_process(self.get_recipients())
            top.destroy()
        else:
            top.destroy()

    def _disable_buttons(self) -> None:
        """Disables all buttons so multiple emails to the same client cannot be sent."""
        self.email_button.config(text="Email(s) sent!")
        self.email_button.config(state="disabled")
        for button in self.buttons:
            button.configure(state="disabled")

    def _make_checkboxes(self) -> None:
        for i in range(len(self.client_list)):
            client = self.client_list[i]
            int_var = tk.IntVar()
            chk_btn = tk.Checkbutton(self.interior, variable=int_var, text=client, anchor="w")
            self.int_var_list.append(int_var)
            self.buttons.append(chk_btn)
            chk_btn.pack(side="top", fill="both")
            if not client.get_email():
                chk_btn.config(state="disabled")

    def _make_labels(self) -> None:
        label = tk.Label(self.interior, text="Select which clients to whom you will send reminder emails.")
        label.pack(side="top")

    def _make_scrollbar(self) -> None:
        self.scrollbar = tk.Scrollbar(self.master, orient=tk.VERTICAL)
        self.scrollbar.pack(side='right', fill="y", expand="false")
        self.canvas = tk.Canvas(self.master,
                                bg='#444444',
                                height=500,
                                width=800,
                                yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand="true")
        self.scrollbar.config(command=self.canvas.yview)
        self.interior = tk.Frame(self.canvas)
        self.canvas.create_window(0, 0, window=self.interior, anchor="nw")
        self.scrollbar.bind('<Configure>', self._set_scroll)

    def _set_scroll(self, event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))


def email_process(recipient_list: List[Client]) -> None:
    """Delivers email list to the send_email function."""

    if recipient_list:
        send_email(recipient_list)
        update_only_emailed_clients(recipient_list)
        remove_fully_contacted_clients()
    else:
        print("No emails were sent.")


def main():
    clients_to_be_contacted = get_clients_to_be_reactivated()
    View(clients_to_be_contacted)


if __name__ == "__main__":
    main()
