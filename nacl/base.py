#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic functions for the nacl package

This module should contain some basic functions, needed
within the nacl package.
Curerntly it does not. This is a design flaw we need to
correct.

There should be moved here:
    * get_users_nacl_conf() from nacl.fileutils

Maybe other functions will fit here in as well.
"""
import salt.config


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

def init_nacl():
    """
    Initialize nacl

    Check contrains like:
        * is an .nacl file present
        * ...
    TODO.
    """
    pass
