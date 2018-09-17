import datetime
import os
import unittest

from add_bulk_clients import add_bulk_clients_to_db
from add_client import get_args, write_to_db
import custom_exceptions
import manage_datetime
from manage_datetime import default_rem_date
import manage_db as mdb


class TestManageDatetime(unittest.TestCase):

    def setUp(self):
        self.valid_date = "1/3/17"
        self.date_with_hyphen = "3-5-18"
        self.valid_datetime = datetime.datetime(18, 3, 1)
        self.separated_date = ["15", "03", "13"]

    def test_separated_date_to_datetime(self):
        self.assertEqual(manage_datetime.separated_date_to_datetime(self.separated_date),
                         datetime.datetime(2015, 3, 13))

    def test_datetime_to_string(self):
        date = datetime.datetime(2018, 11, 2)
        self.assertEqual(manage_datetime.datetime_to_string(date), "11/2/2018")

    def test_date_is_in_future(self):
        self.assertTrue(manage_datetime.date_is_in_future(datetime.datetime(2100, 1, 1)))
        self.assertFalse(manage_datetime.date_is_in_future(datetime.datetime(2017, 1, 1)))

    def test_date_is_in_past(self):
        self.assertFalse(manage_datetime.date_is_in_past(datetime.datetime(2100, 1, 1)))
        self.assertTrue(manage_datetime.date_is_in_past(datetime.datetime(2017, 1, 1)))

    def test_is_rem_date_in_past(self):
        self.assertTrue(manage_datetime.is_rem_date_in_past("3/3/2018"))
        self.assertFalse(manage_datetime.is_rem_date_in_past("3/3/2118"))

    def test_date_is_today(self):
        self.assertTrue(manage_datetime.date_is_today(datetime.datetime.now()))
        self.assertFalse(manage_datetime.date_is_today(datetime.datetime(2017, 1, 1)))

    def test_prepare_date(self):
        self.assertEqual(manage_datetime.prepare_date(self.valid_date, future=True), "1/3/2017")
        self.assertRaises(ValueError, manage_datetime.prepare_date, self.valid_date, past=True)

    def test_validate_date_correct_input(self):
        output = manage_datetime.validate_date(self.valid_date)
        hyphen_date = manage_datetime.validate_date(self.date_with_hyphen)

        self.assertIs(type(output), datetime.datetime)
        self.assertEqual(output.year, 2017)
        self.assertIs(type(hyphen_date), datetime.datetime)
        self.assertEqual(hyphen_date.year, 2018)

    def test_validate_date_invalid_input(self):
        impossible_date_input = "12/45/2017"
        date_too_far_in_past = "9/9/2007"
        incorrect_formatting_input = "a2/13/2017"

        self.assertRaises(ValueError, manage_datetime.validate_date, impossible_date_input)
        self.assertRaises(custom_exceptions.DateTooFarInPast, manage_datetime.validate_date, date_too_far_in_past)
        self.assertRaises(AttributeError, manage_datetime.validate_date, incorrect_formatting_input)


class TestManageDb(unittest.TestCase):

    def setUp(self):
        mdb.add_to_db("Jim", "Smith", "3/12/2017", "3/21/2019", "jim@smith.com", file="test.json")
        mdb.add_to_db("Mary", "Lou", "3/6/2018", "11/6/2018", "mary@lou.com", file="test.json")
        mdb.add_to_db("Humpty", "Dumpty", "5/13/2016", "12/21/2018", "humpty@dumpty.com", file="test.json")

    def test_get_client(self):
        jim = mdb.get_client("Jim", "Smith", "test.json")
        humpty = mdb.get_client("Humpty", "Dumpty", "test.json")

        self.assertEqual(jim[0]["rem date"], "3/21/2019")
        self.assertEqual(humpty[0]["last visit"], "5/13/2016")
        self.assertEqual(humpty[0]["email"], "humpty@dumpty.com")

    def test_delete_client(self):
        mdb.delete_client("Jim", "Smith", file="test.json")
        self.assertEqual(mdb.get_client("Jim", "Smith", "test.json"), [])

    def test_update_times_contacted(self):
        mdb.update_times_contacted("Jim", "Smith", file="test.json")
        self.assertEqual(mdb.get_times_contacted("Jim", "Smith", file="test.json"), 1)

    def test_update_clients_with_rem_date_in_past(self):
        mdb.update_rem_date("Mary", "Lou", "1/1/18", file="test.json")
        mdb.update_clients_with_rem_date_in_past(file="test.json")
        self.assertEqual(mdb.get_times_contacted("Mary", "Lou", file="test.json"), 1)

    def test_delete_db_contents(self):
        mdb.delete_db_contents(file="test.json")
        self.assertEqual(mdb.get_all_db_contents("test.json"), [])

    def tearDown(self):
        os.remove("test.json")


class TestAddClient(unittest.TestCase):

    def test_get_args(self):
        args = get_args(["Jim", "Smith", "2/4/18"])
        args_with_rem_date = get_args(["Jim", "Smith", "2/4/18", "--rem_date", "3/4/19"])
        args_with_all_values = get_args(["Jim", "Smith", "2/4/18", "--rem_date", "3/4/19", "--email", "jim@smith.com"])

        self.assertEqual(args.last_visit, "2/4/18")
        self.assertEqual(args.rem_date,
                         manage_datetime.datetime_to_string(default_rem_date))
        self.assertEqual(args_with_rem_date.first_name, "Jim")
        self.assertEqual(args_with_rem_date.rem_date, "3/4/19")
        self.assertEqual(args_with_all_values.email, "jim@smith.com")

    def test_write_to_db(self):
        correct_args = get_args(["Jim", "Smith", "2/4/18"])
        output = write_to_db(correct_args, db="test.json")
        incorrect_args = get_args(["Jane", "Doe", "asdf"])
        no_output = write_to_db(incorrect_args, db="test.json")
        bad_email = get_args(["asdfjkl", "asdfjkl", "1/1/18", "--rem_date", "3/4/19", "--email", "asdf.com"])
        bad_email_args = write_to_db(bad_email, db="test.json")

        self.assertTrue(output)
        self.assertFalse(no_output)
        self.assertFalse(bad_email_args)

        os.remove("test.json")


class TestAddBulkClients(unittest.TestCase):

    def setUp(self):
        info = [
            'Rob Bob 03/05/2018', 'Susan Smith 1/1/18 4/5/2100', 'Jim Baker 1/1/18 2/2/2100 jim@baker.com',
            '', 'xxx', 'xx yy 4/5/2019', 'a s 03/44/2017', 'adsf asdf 3/3/2017 asdf', 'c d 1/1/2007',
            'a b 1/1/18 4/3/18 a.com', '3 f 3/3/17 1/2/ac'
        ]
        with open("test.txt", "w") as wf:
            for i in info:
                wf.write(i + "\n")

    def add_bulk_clients_to_db(self):
        correct, incorrect = add_bulk_clients_to_db("test.txt", outfile="test.json")
        self.assertEqual(correct, ["Rob Bob", "Susan Smith", "Jim Baker"])
        self.assertEqual(incorrect["Incorrect number of terms"], ["xxx"])
        self.assertEqual(incorrect["Bad date"], ['xx yy 4/5/2019', 'a s 03/44/2017'])
        self.assertEqual(incorrect["Incorrect date formatting"], ['adsf asdf 3/3/2017 asdf', '3 f 3/3/17 1/2/ac'])
        self.assertEqual(incorrect["Date too far in past"], ['c d 1/1/2007'])
        self.assertEqual(incorrect["Email does not contain '@' sign"], ['a b 1/1/18 4/3/18 a.com'])
        os.remove("test.json")
        os.remove("test.txt")


if __name__ == "__main__":
    unittest.main()
