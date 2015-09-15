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
    """ return root of the salt pillars, states, formulas etc. as a list """

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
def get_users_nacl_conf(no_logging=False):
    """ return the users nacl configuration """

    user_home = os.path.expanduser("~")

    __ret = []

    try:
        with open(user_home + '/.nacl') as data_file:
            user_config = json.load(data_file)
        return {'payload': user_config}
    except:
        if no_logging:
            return {'payload': False}

        __ret.append(("FAIL", " ~/.nacl not found or invalid JSON", 3))
        return __ret


def write_users_nacl_conf(json_data=None):
    """ Write down the .nacl file """

    if not json_data:
        raise ValueError('json_data must be provided')

    user_home = os.path.expanduser("~")
    try:
        with open(user_home + '/.nacl', 'w') as json_data_file:
            json.dump(json_data, json_data_file, sort_keys=True, indent=4)
        return True
    except:
        return False


def init_nacl():
    """
    Initialize nacl

    Check contrains like:
        * is an .nacl file present
        * ...
    TODO.
    """
    return True
