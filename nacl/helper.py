#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper functions that aren't fit anywhere else
"""
import random
import string
import sys


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """ Generate an UPPERCASE-DIGIT random string """
    return ''.join(random.choice(chars) for _ in range(size))


def color(level, string):
    """ Colorize strings. Used for pretty outputs. """
    colors = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'DARKCYAN': '\033[36m',
        'INFO': '\033[94m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'GREEN': '\033[92m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }
    return colors[level] + string + colors['ENDC']


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
    It must be "yes" (the default), "no" or None (meaning
    an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def clean_up_dict(clean_dict, ignore_list):
    """
    Remove items from dict that are in ignore_list
    """
    for i in ignore_list:
        clean_dict.pop(i, None)
    return clean_dict


def check_string_to_int(int_string):
    """
    Check whether a string can be converted to int

    This is needed because when 'integers' are provided via the commandline,
    they are strings and have to be converted.
    """
    try:
        if int_string[0] in ('-', '+'):
            return int_string[1:].isdigit()
    except TypeError:
        return int(int_string)

    return int_string.isdigit()
