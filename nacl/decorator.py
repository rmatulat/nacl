#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Some decorators """

import pprint
import sys
from nacl.helper import color


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
            # sys.stderr.write(color('FAIL', 'Function {0} returned None'. format(self._fn.__name__)) + '\n')
            # sys.exit(1)

            # If a decorated function returns None than do nothing.
            # (That might be expected behavior)
            return

        for msg in msgs:

            # we distinguish between tuples with an 3rd argument (sys.exit() exitcode)
            # and no tuples without an exitcode
            if 2 == len(msg):
                level, msg = msg
            elif 3 == len(msg):
                level, msg, exc = msg
            else:
                pass

            if level == 'INFO':
                sys.stdout.write(color(level, msg) + '\n')
            else:
                sys.stderr.write(color(level, msg) + '\n')

            if exc:
                try:
                    exc = int(exc)
                except:
                    raise(ValueError('Exit code must be an integer!'))

                sys.exit(exc)
