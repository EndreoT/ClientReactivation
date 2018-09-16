class Client:
    """A simple client class to easily pass client information between the various helper functions."""

    def __init__(self, first_name: str, last_name: str,
                 last_visit: str, rem_date: str, email: str
                 ):
        self.first_name = first_name
        self.last_name = last_name
        self.last_visit = last_visit
        self.rem_date = rem_date
        self.email = email

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_last_visit(self):
        return self.last_visit

    def get_reminder_date(self):
        return self.rem_date

    def get_email(self):
        return self.email

    def __str__(self):
        return "{} {}, Client's last visit: {}, Client to be reminded on {}, Client's email: {}"\
              .format(self.first_name, self.last_name, self.last_visit, self.rem_date, self.email)
