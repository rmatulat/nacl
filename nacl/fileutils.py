#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains code for file operations in a very broad sense of
    it's meaning."""
import salt.config
# from pprint import pprint


def binary_exists(binary_name):
    """ checks whether a binary exists."""
    from distutils import spawn
    binary_path = spawn.find_executable(binary_name)
    if binary_path:
        return True
    else:
        return False


def get_salt_root_dirs():
    """ return the root of the salt pillars, states, formulas etc."""

    salt_master_config = salt.config.client_config('/etc/salt/master')

    dir_list = []
    # parsing file_roots
    for env, values in salt_master_config['file_roots'].iteritems():
        dir_list.extend(values)

    # parsing pillar root
    for env, values in salt_master_config['pillar_roots'].iteritems():
        dir_list.extend(values)

    return sorted(set(dir_list))
    # return ['/srv/salt/dev']


def get_dir_list_from_filesystem(filter=None):
    """ returns a list of local git repositories directories (.git) """
    import fnmatch
    import os

    matches = []
    if filter is None:
        return matches

    starter = get_salt_root_dirs()
    for start in starter:
        for root, dirnames, filenames in os.walk(start):
            if fnmatch.fnmatch(root, filter):
                matches.append(root)

    return matches


def get_users_nacl_conf():
    """ returns the users nacl configuration """
    from os.path import expanduser
    import json

    user_home = expanduser("~")
    user_config = {}

    with open(user_home + '.nacl') as data_file:
        user_config = json.load(data_file)

    return user_config
