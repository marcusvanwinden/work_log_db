from collections import OrderedDict
from datetime import datetime
from entry import Entry, initialize_database, DATE_FORMAT

import os
import sys


def show_main_menu():
    """Show main menu"""
    menu_range = (1, len(MAIN_MENU))

    while True:
        print_title("Main Menu")
        print_options(MAIN_MENU, docstring=True)
        user_input = validate(get_input(), int, menu_range)
        if user_input:
            MAIN_MENU[user_input]()


def get_entry_values():
    """Get entry values"""
    entry = {}
    for key, question in ENTRY_QUESTIONS.items():
        input_type = int if key == "time" else str

        while True:
            print_title(MAIN_MENU[1].__doc__)
            print(question)
            user_input = validate(get_input(), input_type)
            if user_input or key == "notes":
                entry[key] = user_input
                break

    return entry


def add_entry():
    """Add new entry"""
    entry = get_entry_values()
    return Entry.create(**entry)


def view_entries():
    """View previous entries"""
    if Entry.select():
        menu_range = (1, len(SEARCH_MENU) + 1)
        quit_num = menu_range[1]
        user_input = None

        while user_input != quit_num:
            print_title(view_entries.__doc__)
            print_options(SEARCH_MENU, docstring=True)
            print(f"\n{quit_num}) Return to Main Menu")
            user_input = validate(get_input(), int, menu_range)
            if user_input in SEARCH_MENU:
                search_results = SEARCH_MENU[user_input]()
                return print_entries(search_results)

    else:
        return print_error("No previous entries. Please add an entry first.")


def print_entries(entries):
    """Print entries"""
    if entries:
        try:
            entries = [entry for entry in entries.dicts()]
        except AttributeError:
            pass
        curr_i, last_i = (0, len(entries))
        user_input = None

        while user_input != "r":
            print_title("Results")
            print(f"Result {curr_i + 1} of {last_i}\n")
            for key, value in entries[curr_i].items():
                print(f"{key.capitalize():9}: {value}")
            print("\n[B]ack, [N]ext, [E]dit, [D]elete, [R]eturn to Main Menu")
            user_input = validate(get_input(), str).lower()
            menu = ["b", "n", "e", "d", "r"]
            if user_input in menu:
                if user_input == "b" and curr_i > 0:
                    curr_i -= 1
                elif user_input == "n" and curr_i < last_i - 1:
                    curr_i += 1
                elif user_input == "e":
                    entries[curr_i] = edit_entry(entries[curr_i])
                elif user_input == "d":
                    return delete_entry(entries, entries[curr_i])

    else:
        return print_error("No entries found.")


def edit_entry(edit_result):
    """Edit entry"""
    new_entry = edit_result.copy()
    edit_key = None
    edit_value = None
    optional = ["notes"]
    ignore = ["id"]

    while edit_key not in edit_result or edit_key in ignore:
        print_title(edit_entry.__doc__)
        print("Type the key you want to edit.\n")
        for key, value in edit_result.items():
            if key not in ignore:
                print(f"{key.capitalize():9}: {value}")
        edit_key = validate(get_input(), str).lower()
        if edit_key not in edit_result or edit_key in ignore:
            print_error("Input not a valid key.")

    if edit_key == "time":
        input_type = int
    elif edit_key == "date":
        input_type = datetime
    else:
        input_type = str

    while not edit_value:
        print_title(edit_entry.__doc__)
        print(EDIT_QUESTIONS[edit_key])
        edit_value = validate(get_input(), input_type)
        if edit_key in optional:
            break

    new_entry[edit_key] = edit_value
    Entry.update(**{edit_key: edit_value}).where(Entry.id == new_entry["id"]).execute()
    return new_entry


def delete_entry(results, del_result):
    """Delete entry"""
    Entry.delete_by_id(del_result["id"])
    results.remove(del_result)
    return print_entries(results)


def find_by_employee():
    """Find by employee"""
    entries = Entry.select(Entry.employee)
    employees = list(sorted(set(entry.employee for entry in entries)))
    user_input = None

    while not user_input:
        print_title(find_by_employee.__doc__)
        print("Suggestions:\n")
        print_options(employees)
        print("\nType in a name from the list above.")
        user_input = validate(get_input())

    matches = []
    for employee in employees:
        if user_input.lower() in employee.lower():
            matches.append(employee)
    if len(matches) <= 1:
        results = Entry.select().where(Entry.employee << matches)
    else:
        user_input = None
        menu_range = (1, len(matches))

        while not user_input:
            print_title("Found Multiple Names")
            print("Select one of the following employees.\n")
            print_options(matches)
            user_input = validate(get_input(), int, menu_range)

        results = Entry.select().where(
            Entry.employee == matches[user_input - 1])
    return results


def find_by_date():
    """Find by date"""
    entries = Entry.select(Entry.date)
    dates = list(sorted(set(entry.date for entry in entries), reverse=True))
    user_input = None

    while not user_input:
        print_title(find_by_date.__doc__)
        print_options(dates)
        user_input = validate(get_input(), int, (1, len(dates)))

    results = Entry.select().where(Entry.date == dates[user_input - 1])
    return results


def find_by_date_range():
    """Find by date range"""
    beg_date = None
    end_date = None

    while not beg_date:
        print_title(find_by_date_range.__doc__)
        print("Begin date (mm/dd/yyyyy):")
        beg_date = validate(get_input(), datetime)

    while not end_date:
        print_title(find_by_date_range.__doc__)
        print("End date (mm/dd/yyyy):")
        end_date = validate(get_input(), datetime)

    results = Entry.select().where(
        Entry.date.between(beg_date, end_date))
    return results


def find_by_time():
    """Find by time"""
    entries = Entry.select(Entry.time)
    times = list(sorted(set(entry.time for entry in entries), reverse=True))
    user_input = None

    while not user_input:
        print_title(find_by_time.__doc__)
        print("Suggestions:\n")
        print_options(times)
        print("\nType in an amount of minutes from the list above.")
        user_input = validate(get_input(), int)

    results = Entry.select().where(Entry.time == user_input)
    return results


def find_by_term():
    """Find by term"""
    user_input = None

    while not user_input:
        print_title(find_by_term.__doc__)
        print("Please type a title or note.")
        user_input = validate(get_input())

    results = Entry.select().where(
        Entry.task.contains(user_input) | Entry.notes.contains(user_input))
    return results


def validate(value, type=str, range=None):
    """Validate a value against type (and range) criteria"""
    if type == datetime:
        try:
            datetime.strptime(value, DATE_FORMAT)
            return value
        except ValueError:
            print_error("Value is not a valid date.")
            return False
    elif type == int:
        try:
            value = int(value)
            if range:
                if value >= range[0] and value <= range[1]:
                    return value
                print_error("Value is not a menu option.")
                return False
            return value
        except ValueError:
            print_error("Value is not an integer.")
            return False
    elif type == str:
        return value.strip()


def get_input():
    """Get a user's input"""
    return input("\n> ")


def clear_screen():
    """Clear the screen"""
    os.system("cls" if os.name == "nt" else "clear")


def print_title(title):
    """Format string to title and print to the screen"""
    clear_screen()
    print("{0}\n{1}\n{0}\n".format(("-" * 35), title.title()))


def print_options(options, docstring=False):
    """Print key, option for a options dictionary"""
    if isinstance(options, dict):
        for key, option in options.items():
            if docstring:
                print(f"{key}) {option.__doc__}")
            else:
                print(f"{key}) {option}")
    elif isinstance(options, list):
        for i, option in enumerate(options, 1):
            print(f"{i}) {option}")


def print_error(message):
    """Print error message to the screen"""
    clear_screen()
    print_title("Error")
    print(message)
    input("\nPress Enter to continue... ")


def quit_program():
    """Quit program"""
    clear_screen()
    sys.exit()


MAIN_MENU = OrderedDict([
    (1, add_entry),
    (2, view_entries),
    (3, quit_program),
])

SEARCH_MENU = OrderedDict([
    (1, find_by_employee),
    (2, find_by_date),
    (3, find_by_date_range),
    (4, find_by_time),
    (5, find_by_term),
])

ENTRY_QUESTIONS = OrderedDict([
    ("employee", "What is your name?"),
    ("task", "What is the task?"),
    ("time", "How long did you work on it? (minutes)"),
    ("notes", "Any additional notes? (optional)"),
])

EDIT_QUESTIONS = OrderedDict([
    ("employee", "What is the new [employee] value?"),
    ("task", "What is the new [task] value?"),
    ("time", "What is the new [time] value? (minutes)"),
    ("notes", "What is the new [additional notes] value? (optional)"),
    ("date", "What is the new [date] value? (yyyy-mm-dd)"),
])

if __name__ == "__main__":
    initialize_database()
    show_main_menu()
