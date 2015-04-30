#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import string
from subprocess import Popen, PIPE


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
