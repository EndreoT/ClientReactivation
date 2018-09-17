# ClientReactivation
Reminds business to reactivate old clients and prompt them to make an appointment by sending a reminder email.

Businesses often lose business from clients who cancel appointments and do not reschedule, or from clients who say they will make a new 
appointment but forget to do so. This project aims to solve that by setting up a reminder system to alert a business to when a client 
should be contacted for reactivation. 

Client infomation is stored in a NOSQL database via the tinydb package. Installation instructions and furter information on the
database can be found at https://github.com/msiemens/tinydb. If you are installing tinydb using an Anaconda virtual environment, the
easiest way I found is to install with conda run using the command: conda install -c conda-forge tinydb

There are two primary ways to add client information to the database: add_client.py uses the command line to enter clients one at a time.
add_bulk_clients.py is used when the user wishes to populate the bulk_client_staging text file with line separated client information. 
All clients must have a first and last name, as well as a last visit date. A reminder date and email address are optional, but recommended.

__main__.py brings up a GUI and displays which clients should be contacted based on their reminder date. The user can then send 
reminder emails directly from this interface. Make sure to edit your information(email, login password, etc.) in manage_email.py

It is recommended to schedule __main__.py to run once a day using a task scheduling program so as to maximize client contact. Windows users
can use Task Scheduler, Cron Jobs for Linux, and Automator for Mac.

