#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Working with files

Contains code for file operations in a very broad sense of
it's meaning.
"""
import salt.config
from distutils import spawn
from nacl.decorator import log
import fnmatch
import os
import json


def binary_exists(binary_name):
    """ checks whether a binary exists. """
    binary_path = spawn.find_executable(binary_name)
    if binary_path:
        return True
    else:
        return False


def get_salt_root_dirs():
    """
    return the root of the salt pillars, states, formulas etc.

    TODO: Move this to nacl.base
    It looks like this is not a typical file related opetions and maybe
    better placed at nacl.base.
    """

    salt_master_config = salt.config.client_config('/etc/salt/master')

    dir_list = []

    # parsing file_roots
    for env, values in salt_master_config['file_roots'].iteritems():
        dir_list.extend(values)

    # parsing pillar root
    for env, values in salt_master_config['pillar_roots'].iteritems():
        dir_list.extend(values)

    return sorted(set(dir_list))


def get_dir_list_from_filesystem(filter=None):
    """
    Returns a list of salt directories

    Its purpose is to return a list of pillar- and state directories.

    TODO:
    It is only used to return directories with git repos in it.
    So we can remove the filter=None parameter and rename the function to
    make it a bit more descriptive.
    """

    matches = []
    if filter is None:
        return matches

    starter = get_salt_root_dirs()

    for start in starter:
        for root, dirnames, filenames in os.walk(start):
            if fnmatch.fnmatch(root, filter):
                matches.append(root)

    return matches


@log
def get_users_nacl_conf():
    """
    returns the users nacl configuration

    TODO: Move this to nacl.base
    It looks like this is not a typical file related opetions and maybe
    better placed at nacl.base.
    """

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
