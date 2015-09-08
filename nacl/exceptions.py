#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Custom exceptions

For clarity it is intended to use custom exceptions whenever
appropriate.
"""


class GitCallError(Exception):
    """ Raise this when something is wrong while calling git. """
    pass
