from datetime import datetime
from entry import Entry
from peewee import *
from unittest import main, TestCase
from unittest.mock import patch

import app

TEST_DB = SqliteDatabase(':memory:')

MODELS = [Entry]

TEST_ENTRY = {
    "employee": "Marcus",
    "task": "Programming",
    "time": 100,
    "notes": "Project #4",
}

TEST_ENTRY_2 = {
    "employee": "Menno",
    "task": "Designing",
    "time": 50,
    "notes": "VVD",
}


class WorkLogTests(TestCase):

    def setUp(self):
        # Connect to the test database and create tables.
        TEST_DB.bind(MODELS, bind_refs=False, bind_backrefs=False)
        TEST_DB.connect()
        TEST_DB.create_tables(MODELS)

    def mock_input(self, prompt):
        # Provides values for the various functions that need input.
        return next(self.test_values)

    def test_show_main_menu(self):
        # Test if the script shows the main menu and then quit the program [3].
        self.test_values = (value for value in ["3"])
        with patch("builtins.input", self.mock_input):
            with self.assertRaises(SystemExit):
                app.show_main_menu()
                # Test if the menu prints the title.
                with patch("app.print_title") as print_title:
                    self.assertTrue(print_title.called)
                # Test if the menu prints the options.
                with patch("app.print_options") as print_options:
                    self.assertTrue(print_options.called)
                # Testing after this point is difficult
                # since the main menu runs a loop.

    def test_get_entry_values(self):
        # Test if the function returns an object with the given values.
        self.test_values = (value for value in TEST_ENTRY.values())
        with patch("builtins.input", self.mock_input):
            result = app.get_entry_values()
        self.assertEqual(result, TEST_ENTRY)

    def test_add_entry(self):
        # Test if the functions returns an Entry with the given values.
        self.test_values = (value for value in TEST_ENTRY.values())
        with patch("builtins.input", self.mock_input):
            result = app.add_entry()
        self.assertIsInstance(result, Entry)

    def test_view_entries(self):
        # Test if the functions prints an error when the user tries to search
        # for entries when there are none in the database.
        with patch("app.print_error") as print_error:
            app.view_entries()
        self.assertTrue(print_error.called)

    def test_print_entries(self):
        # Test if entries print to the screen and if the menu works [n, b].
        # Eventually the script will return to the main menu [r] and quit [3].
        Entry.create(**TEST_ENTRY)
        results = Entry.select()
        self.test_values = (value for value in ["n", "b", "r", "3"])
        with patch("builtins.input", self.mock_input):
            app.print_entries(results)

    def test_edit_entry(self):
        # Test if every key can be edited (except for id).
        entry = Entry.create(**TEST_ENTRY)
        entry = {
            "id": entry.id,
            "employee": entry.employee,
            "task": entry.task,
            "time": entry.time,
            "notes": entry.notes,
            "date": entry.date,
        }
        new_values = [
            "employee", "Menno",
            "task", "Designing",
            "time", 50,
            "notes", "VVD",
            "date", "01/01/2001"
        ]
        results = []
        self.test_values = (value for value in new_values)
        for _ in range(len(entry) - 1):
            with patch("builtins.input", self.mock_input):
                results.append(app.edit_entry(entry))
        self.assertEqual(results[0]["employee"], new_values[1])
        self.assertEqual(results[1]["task"], new_values[3])
        self.assertEqual(results[2]["time"], new_values[5])
        self.assertEqual(results[3]["notes"], new_values[7])
        self.assertEqual(results[4]["date"], new_values[9])

    def test_find_by_employee(self):
        # Test if an entry can be found through a single name.
        entry_1 = Entry.create(**TEST_ENTRY)
        self.test_values = (value for value in [entry_1.employee])
        with patch("builtins.input", self.mock_input):
            results = app.find_by_employee()
        self.assertEqual(results[0], entry_1)

        # If the user types in [m] and there are two employees with that
        # letter in their name, test if the user can select an option [2].
        entry_2 = Entry.create(**TEST_ENTRY_2)
        self.test_values = (value for value in ["m", "2"])
        with patch("builtins.input", self.mock_input):
            results = app.find_by_employee()
        self.assertEqual(results[0], entry_2)

    def test_find_by_date(self):
        # Test if an entry can be found through a single date.
        entry = Entry.create(**TEST_ENTRY)
        self.test_values = (value for value in ["1"])
        with patch("builtins.input", self.mock_input):
            results = app.find_by_date()
        self.assertEqual(results[0], entry)

    def test_find_by_date_range(self):
        # Test if an entry can be found through a date range.
        entry = Entry.create(**TEST_ENTRY)
        self.test_values = (value for value in ["01/01/2019", "12/31/2019"])
        with patch("builtins.input", self.mock_input):
            results = app.find_by_date_range()
        self.assertEqual(results[0], entry)

    def test_find_by_time(self):
        # Test if an entry can be found through time spent.
        entry = Entry.create(**TEST_ENTRY)
        self.test_values = (value for value in [entry.time])
        with patch("builtins.input", self.mock_input):
            results = app.find_by_time()
        self.assertEqual(results[0], entry)

    def test_find_by_term(self):
        # Test if an entry can be found through a title or note.
        entry = Entry.create(**TEST_ENTRY)
        self.test_values = (value for value in [entry.task])
        with patch("builtins.input", self.mock_input):
            results = app.find_by_term()
        self.assertEqual(results[0], entry)

    def test_validate(self):
        # Test if values are successfully validated.
        self.assertTrue(app.validate("01/01/2019", datetime))
        self.assertTrue(app.validate("1", int))
        self.assertTrue(app.validate("string", str))
        # The following inputs are needed to confirm the error messages.
        self.test_values = (value for value in ["x", "x", "x"])
        with patch("builtins.input", self.mock_input):
            self.assertFalse(app.validate("x", int))
            self.assertFalse(app.validate("x", datetime))
            self.assertFalse(app.validate(5, int, (1, 2)))

    def test_print_options(self):
        self.assertFalse(app.print_options({1: "x"}))
        self.assertFalse(app.print_options({1: "x"}, True))

    def test_quit_program(self):
        # Test if the script quits the program.
        with self.assertRaises(SystemExit):
            app.quit_program()

    def tearDown(self):
        # Empty the database and clear the screen.
        TEST_DB.drop_tables(MODELS)
        TEST_DB.close()
        app.clear_screen()


if __name__ == "__main__":
    main()
