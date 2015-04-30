#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains code for file operations in a very broad sense of
    it's meaning."""
import vendor.yaml as yaml
# from pprint import pprint


def binary_exists(binary_name):
    """ checks whether a binary exists."""
    from distutils import spawn
    binary_path = spawn.find_executable(binary_name)
    if binary_path:
        return True
    else:
        return False


def get_salt_start_dir():
    """ return the root of the salt pillars, states, formulas etc."""

    # read /etc/salt/master to gather state and pillar dirs
    with open('/etc/salt/master') as data_file:
        salt_master_config = yaml.load(data_file)

    dir_list = []
    # parsing file_roots
    for environments in salt_master_config['file_roots']:
        for env in salt_master_config['file_roots'][environments]:
            dir_list.append(env)

    # parsing pillar root
    for environments in salt_master_config['pillar_roots']:
        for env in salt_master_config['pillar_roots'][environments]:
            dir_list.append(env)

    return sorted(set(dir_list))
    # return ['/srv/salt/dev']


def get_dir_list_from_filesystem(filter=None):
    """ returns a list of local git repositories directories (.git) """
    import fnmatch
    import os

    matches = []
    if filter is None:
        return matches

    starter = get_salt_start_dir()
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
