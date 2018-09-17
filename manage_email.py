"""Use to send reminder emails to clients. Uses client's personal name in each email."""

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from string import Template
from typing import List

from client import Client

"""*****************BE AWARE YOUR EMAIL PASSWORD WILL BE WRITTEN IN THIS FILE*****************"""

# Modify these constants
sender_name = "Business owner name"
contact_number = "123-456-7890"
sender_email = "**********"
sender_password = "**********"

# For gmail you will need to allow less secure apps to access your account. Also, use the following defaults:
# host_address = 'smtp.gmail.com'
# port_number = 465

host_address = 'smtp.gmail.com'
port_number = 465


def validate_email(email: str) -> bool:
    """Returns false if email does not contain '@' sign."""

    if not email:
        return True
    if "@" in email:
        return True
    return False


def create_template(filename) -> Template:
    """Returns a Template object to be used in crafting emails."""

    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


def create_message(recipient_list: List[Client], business_number: str, your_name: str) ->List[MIMEMultipart]:
    """
    Creates an email message text file. Returns a list of MIMEMultipart messages for each recipient with an email.
    Make sure to edit message.txt with your custom message.
    """

    msg_list = []
    for recipient in recipient_list:
        if recipient.get_email():
            message_template = create_template('message.txt')
            msg = MIMEMultipart()
            message = message_template.substitute(
                PERSON_NAME=recipient.get_first_name(),
                PHONE=business_number, YOUR_NAME=your_name)
            msg['From'] = sender_email
            msg['To'] = recipient.get_email()
            msg['Subject'] = "We miss you!"
            msg.attach(MIMEText(message, 'plain'))
            msg_list.append(msg)
    return msg_list


def make_email_list(recipient_list: List[Client]) -> List[str]:
    """Returns an email list for all clients that have an email."""

    return [client.get_email() for client in recipient_list if client.get_email()]


def send_email(recipient_list: List[Client]) -> None:
    """Logs in and sends an email to each recipient in the recipient list."""

    try:
        email_list = make_email_list(recipient_list)
        msg_list = create_message(recipient_list, contact_number, sender_name)
        server = smtplib.SMTP_SSL(host_address, port_number)
        server.ehlo()
        server.login(sender_email, sender_password)
        for i in range(len(recipient_list)):
            server.send_message(msg_list[i], sender_email, email_list[i])
        server.close()
        print('Email(s) sent!')
    except:
        print("Something went wrong!")
