#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import string
from subprocess import Popen, PIPE
import sys


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def run(args, env=None):
    """ @args: list
        @env: dict
        Calling subprocesses
    """
    if env is not None:
        env = env
    else:
        env = {}

    p = Popen(args, stdout=PIPE, stderr=PIPE, env=env)
    output, err = p.communicate()

    if err:
        print("ERROR: " + err)
        print(Popen(['pwd']))
        raise Exception('git call should not return errors')
    return output


def color(level, string):
    """ Colorize strings """
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
    """Ask a yes/no question via raw_input() and return their answer.

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
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z