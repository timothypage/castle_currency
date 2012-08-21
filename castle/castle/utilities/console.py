# -*- coding: utf-8 -*
from __future__ import print_function


# TODO alternatives for print? sys.out?
def ask_boolean(message, fail_threshold=5):
    """
    Standard yes / no query for command line input.
    Will return false if fail_threshold is reached.
    """
    # Guarantee that there is a message and that it ends in a space
    if not message:
        "'Yes' or 'no'? "
    elif message[-1] != " ":
        message += " "

    # TODO allow user to set trues and falses?
    trues = set(['y', 'yes', 'true', 't', '1', 'sure', 'okay'])
    falses = set(['n', 'no', 'false', 'f', '0', 'nope', 'cancel'])
    fails = 0

    def closure(fails):
        answer = (raw_input(message)).lower()
        if answer in trues:
            return True
        elif answer in falses:
            return False
        else:
            fails += 1
            if fails >= fail_threshold:
                print("Exiting...")
                return False
            print("Please answer 'yes' or 'no'")
            return closure(fails)

    return closure(fails)


def display_counter(counter):
    """
    Output a collections.Counter object to the console
    """
    print("The following operations will be performed:")
    count_row = "  * {action:<16} {count}"
    # TODO iterate through the actions and determine optimal length
    for action, count in counter.items():
        print(count_row.format(action=action.replace("_", " "), count=count))