#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic functions for the nacl package

This module should contain some basic functions, needed
within the nacl package.
"""
import salt.config
from nacl.decorator import log
import json
import os


def get_salt_root_dirs():
    """ return the root of the salt pillars, states, formulas etc. """

    salt_master_config = salt.config.client_config('/etc/salt/master')

    dir_list = []

    # parsing file_roots
    for env, values in salt_master_config['file_roots'].iteritems():
        dir_list.extend(values)

    # parsing pillar root
    for env, values in salt_master_config['pillar_roots'].iteritems():
        dir_list.extend(values)

    return sorted(set(dir_list))


@log
def get_users_nacl_conf():
    """ returns the users nacl configuration """

    user_home = os.path.expanduser("~")
    user_config = {}
    _ret = []

    try:
        with open(user_home + '/.nacl') as data_file:
            user_config = json.load(data_file)
        return {'direct_out': user_config}
    except:
        _ret.append(("FAIL", " ~/.nacl not found or invalid JSON", 3))
        return _ret


def init_nacl():
    """
    Initialize nacl

    Check contrains like:
        * is an .nacl file present
        * ...
    TODO.
    """
    pass
