#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Custom decorators

TODO: Move everything to blessings
SEE: https://pypi.python.org/pypi/blessings
"""

import sys
from nacl.helper import color
from vendor.blessings import Terminal
import pprint


def log(func):
    """
    Log decorator implemented as function

    This code was added after class Log() because of problems during
    unittesting nacl.flow.NaclFlow.
    The problem: The discriptor protocol implementation with __get__() and
    functools.partials leads to problems in addressing Log._fn() under
    test, because self is masked with the decorated class functions
    self (of class NaclFLow). So we are unable to call the function under
    test undecorated.
    """

    def wrapper(*args, **kwargs):
        level = 'INFO'
        msg = 'Not set'
        exc = None
        msgs = func(*args, **kwargs)

        # maybe there is a function that prints stuff to the terminal in
        # case of failures, BUT return data structures like dicts etc as well.
        # In this case, we need a way to distinguish between
        # both possibilities.
        # So if you have a function with the @log decorator,
        # but in some occasions it has to return data, then wrap this data
        # in a dict like so:
        # return {'payload': my_data}
        # 'payload' is the key to return whatever you want.

        try:
            return msgs['payload']
        except:
            pass

        if not msgs:
            # If a decorated function returns None than do nothing.
            # (That might be expected behavior)
            return

        for msg in msgs:

            # we distinguish between tuples with an 3rd argument
            # (sys.exit() exitcode)
            # and no tuples without an exitcode
            show_lvl = 'INFO'
            if 2 == len(msg):
                level, msg = msg
            elif 3 == len(msg):
                level, msg, exc = msg
                show_lvl = 'WARN'
            else:
                raise ValueError('tuple must contain 2 or 3 elements!')

            if level == 'INFO':
                sys.stdout.write(u'[ {0} ] {1}'.format(show_lvl, color(level, msg)) + '\n')
            else:
                sys.stderr.write(u'[ {0} ] {1}'.format(show_lvl, color(level, msg)) + '\n')

            if exc:
                try:
                    exc = int(exc)
                except:
                    raise(ValueError('Exit code must be an integer!'))

                sys.exit(exc)

    wrapper._fn = func
    return wrapper


class ListLine(object):
    """
    Print out a single, pretty line about a single git Repository

    This is only used for nacl-git l: print out a line
    with information about a repository.
    There is no general usecase except for this single purpose.
    So it's nasty...
    """

    def __init__(self, fn):
        self._fn = fn
        self.t = Terminal()

    def __call__(self, *args, **kwargs):
        __ret = self._fn(*args, **kwargs)

        if not __ret:
            return

        if __ret['status'] == 'Clean':
            st_level = 'UNDERLINE'
        else:
            st_level = 'GREEN'

        # colorize merge_status
        if __ret['merge_status'] == '(merged)':
            m_s_level = 'INFO'
        else:
            m_s_level = 'FAIL'

        # colorize pull_push
        if __ret['pull_push'] == "Up-to-date":
            p_p_level = 'GREEN'
        else:
            p_p_level = 'FAIL'

        # sys.stdout.write(
        s = u'{0}{1}{2}{3}{4}{5}\n'.format(
            self.t.move_x(0) + color('WARNING', __ret['dir_name']),
            self.t.move_x(51) + color('GREEN', __ret['branch']),
            self.t.move_x(57) + color(m_s_level, __ret['merge_status']),
            self.t.move_x(67) + color(st_level, __ret['status']),
            self.t.move_x(83) + color(p_p_level, __ret['pull_push']),
            self.t.move_x(99) + color('DARKCYAN', __ret['all_branches'])).encode()

        sys.stdout.write(s.decode('utf-8'))
