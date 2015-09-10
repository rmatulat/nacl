#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
nacl-setup module

This module handles all the stuff for setting up the nacl-* scripts.
That contains by now:
  * Setting up git. This is needed, because we like to distinguish between
    developers.
  * Setting up the .nacl.conf file.
"""

import nacl.git
import nacl.helper
from nacl.helper import color
from nacl.exceptions import GitCallError
import sys
import pprint


def setup_git():
    user_name = nacl.git.get_user_name()
    user_email = nacl.git.get_user_email()

    user_name = nacl.helper.input_wrapper(
        'Please enter your name for git usage (e.g. John Doe)',
        user_name)

    # We do not make any validation here.
    # Shame on me!
    user_email = nacl.helper.input_wrapper(
        'Please enter your email adress for git usage '
        '(e.g. john.doe@example.com)',
        user_email.lower())

    try:
        nacl.git.set_user_name(user_name)
        nacl.git.set_user_email(user_email)

        sys.stdout.write(u'Git preferences updated to: \n')
        sys.stdout.write(u'{0}\n{1}\n'.format(
            color('INFO', nacl.git.get_user_name()),
            color('FAIL', nacl.git.get_user_email())))
    except GitCallError as e:
        sys.stdout.write(u'Something went wrong: {0}'.format(e.message))

    return True


def setup_nacl():
    return True
