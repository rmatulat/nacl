#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""nacl-setup

Usage:
  nacl-setup.py git
  nacl-setup.py nacl
  nacl-setup.py (-h | --help)
  nacl-setup.py --version

Options:
  git               Setup your local git, e.g. name and email-adress
  nacl              Setup nacl itself (the .nacl.conf file)
  -h --help         Show this screen.
  --version         Show version.

"""
from nacl.setup import setup_git
from nacl.setup import setup_nacl
from vendor.docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='nacl-setup version 0.1')
    # print(arguments)

if arguments['git']:
    setup_git()

if arguments['nacl']:
    setup_nacl()
