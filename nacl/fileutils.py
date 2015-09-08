#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Working with files

Contains code for file operations in a very broad sense of
it's meaning.
"""
from distutils import spawn
from nacl.base import get_salt_root_dirs
import fnmatch
import os
# import pprint


def binary_exists(binary_name):
    """ checks whether a binary exists. """
    binary_path = spawn.find_executable(binary_name)
    if binary_path:
        return True
    else:
        return False


def get_dir_list_from_filesystem(filter='*.git'):
    """
    Returns a list of salt directories

    Its default purpose is to return a list of pillar- and state
    git directories.
    Maybe we like to use this function later on to find directories with *.sls
    files in them.
    """

    matches = []
    starter = get_salt_root_dirs()

    for start in starter:
        for root, dirnames, filenames in os.walk(start):
            if fnmatch.fnmatch(root, filter):
                matches.append(root)

    return matches
