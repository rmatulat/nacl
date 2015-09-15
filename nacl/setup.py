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

import sys
import nacl.base
import nacl.git
import nacl.helper
import pprint
from nacl.exceptions import GitCallError


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
            nacl.helper.color('INFO', nacl.git.get_user_name()),
            nacl.helper.color('FAIL', nacl.git.get_user_email())))
    except GitCallError as e:
        sys.stdout.write(u'Something went wrong: {0}'.format(e.message))

    return True


def setup_nacl():
    """
    Setup the .nacl file

    This might be true to create a new .nacl file or just to change an
    existing file instead.
    """

    user_config = nacl.base.get_users_nacl_conf(no_logging=True)

    # If there is no .nacl present (or the JSON data is broken) than
    # provide some defaults.
    # This is the most easy way I came up with, handling defaults of several
    # questions. More elegant suggestions are welcome!
    if not user_config:
        user_config = {
            'gitapiserver': 'https://gitlab.example.com',
            'gitapitoken': '<MyAweSomeToken>',
            'gitgroup': 'saltstack',
            'proxy': '',
            'ignore_repositories': [
                'git@gitlab.example.com:saltstack/example.git']
        }

    # We have to handle each question for a value a little differently because
    # there are changing needs in asking questions and/or parse the answer.

    # 1. Ask for the Gitlab Server. This one will used in further question.
    user_config['gitapiserver'] = nacl.helper.input_wrapper(
        'Please give the URL of your Gitlab Server '
        'like "https://gitlab.example,com"',
        user_config['gitapiserver']
    )

    # 2. Get the API token
    user_config['gitapitoken'] = nacl.helper.input_wrapper(
        '\nPlease give your Gitlap API token. \n'
        'You will find it under {0}{1} '.format(
            user_config['gitapiserver'],
            '/profile/account'
        )
    )

    # 3. What's the gitgroup
    user_config['gitgroup'] = nacl.helper.input_wrapper(
        '\nWhat is the name of the Gitlab group? ',
        user_config['gitgroup']
    )

    # 4. Any proxy setting needed?
    configure_proxy = nacl.helper.query_yes_no(
        'Do you need a proxy to connect to the internet?',
        'no')
    if configure_proxy:
        user_config['proxy'] = nacl.helper.input_wrapper(
            '\nURL of your proxy may goes here (like '
            '"http://proxy.example.com:8000") ',
            user_config['proxy']
        )

    # 5. Following repositories should be ignored
    configure_ignorelist = nacl.helper.query_yes_no(
        '\nDo you want to configure a list of ignored '
        'git repositories? This is handy when there are \n'
        'repositories under your gitlab group "{0}" that should '
        'be ignored by nacl.'.format(user_config['gitgroup']),
        'no')

    if configure_ignorelist:
        user_config['ignore_repositories'] = nacl.helper.input_wrapper(
            '\nThe list must be provided as a comma separated list, like \n"{0}"'.
            format(
                nacl.helper.color(
                    'INFO',
                    'git@gitlab.ex.com:saltstack/foo.git, git@gitlab.ex.com:saltstack/bar.git')),
            ', '.join(user_config['ignore_repositories'])
        )

        user_config['ignore_repositories'] = user_config['ignore_repositories'].split(',')

    if nacl.base.write_users_nacl_conf(user_config):
        sys.stdout.write('\n.nacl file written\n')
    else:
        sys.stderr.write('\nSomething went wrong!\n')

    return True
