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


def binary_exists(binary_name):
    """ checks whether a binary exists. """
    binary_path = spawn.find_executable(binary_name)
    if binary_path:
        return True
    else:
        return False


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
