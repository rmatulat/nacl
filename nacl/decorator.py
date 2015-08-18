#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Some decorators
TODO: Move everything to blessings
SEE: https://pypi.python.org/pypi/blessings
"""

import pprint
import sys
from nacl.helper import color
from vendor.blessings import Terminal
import functools


class Log(object):
    """
    Log decorator

    The decorated function has to return a list of tuples, e.g.

        return [('INFO', 'My awesome message')]

    So the first element of the tuple is the logging level,
    the 2nd parameter is the message itself.

    There is a third tuble element possible. That 3rd element has to be
    an integer and stands for the exitcode - usually provided if the
    exitcode has to be != 0.

    Setting an exitcode means the for loop of displaying logmessages
    will be left with sys.exit()

    By now we just log to the commandline, but it is possible
    to exrend this later to log to files etc.

    """
    def __init__(self, fn):
        self._fn = fn

    def __call__(self, *args, **kwargs):
        level = 'INFO'
        msg = 'Not set'
        exc = None
        msgs = self._fn(*args, **kwargs)

        if not msgs:
            # If a decorated function returns None than do nothing.
            # (That might be expected behavior)
            return

        for msg in msgs:

            # we distinguish between tuples with an 3rd argument (sys.exit() exitcode)
            # and no tuples without an exitcode
            show_lvl = 'INFO'
            if 2 == len(msg):
                level, msg = msg
            elif 3 == len(msg):
                level, msg, exc = msg
                show_lvl = 'WARN'
            else:
                raise ValueError('tuble must contain 2 or 3 elements!')

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

    def __get__(self, instance, instancetype):
        """Implement the descriptor protocol to make decorating instance
        method possible.
        See : http://stackoverflow.com/questions/5469956/python-decorator-self-is-mixed-up
        """

        # Return a partial function with the first argument is the instance
        #   of the class decorated.
        return functools.partial(self.__call__, instance)


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
        _ret = self._fn(*args, **kwargs)

        if not _ret:
            return

        if _ret['status'] == 'Clean':
            st_level = 'UNDERLINE'
        else:
            st_level = 'GREEN'

        # colorize merge_status
        if _ret['merge_status'] == '(merged)':
            m_s_level = 'INFO'
        else:
            m_s_level = 'FAIL'

        # colorize pull_push
        if _ret['pull_push'] == "Up-to-date":
            p_p_level = 'GREEN'
        else:
            p_p_level = 'FAIL'

        # sys.stdout.write(
        s = u'{0}{1}{2}{3}{4}{5}\n'.format(
            self.t.move_x(0) + color('WARNING', _ret['dir_name']),
            self.t.move_x(51) + color('GREEN', _ret['branch']),
            self.t.move_x(57) + color(m_s_level, _ret['merge_status']),
            self.t.move_x(67) + color(st_level, _ret['status']),
            self.t.move_x(83) + color(p_p_level, _ret['pull_push']),
            self.t.move_x(99) + color('DARKCYAN', _ret['all_branches'])).encode()

        sys.stdout.write(s.decode('utf-8'))
