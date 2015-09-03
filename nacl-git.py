#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""nacl-git

Usage:
  nacl-git.py (list | l)
  nacl-git.py (branch | b) [BRANCH]
  nacl-git.py (checkout | c) [BRANCH]
  nacl-git.py mergeall
  nacl-git.py (merge | m)
  nacl-git.py (prune | pr)
  nacl-git.py (remote-diff | rd)
  nacl-git.py (compare-remote | cr)
  nacl-git.py (-h | --help)
  nacl-git.py --version

Options:
  list              List all salt related local respositories
  branch            Show current branch. If BRANCH is provided it will create BRANCH with --track
  checkout          Checkout master or BRANCH
  mergeall          Merge all diverged branches of all pillars and modules
  merge             Merges remote into local branch (e.g. 'git merge --ff-only')
  prune             Removes staled remote refs
  remote-diff        Show diff between local and remote
  compare-remote    Are all remote git repos on our local filesystem?
  -h --help         Show this screen.
  --version         Show version.

"""
# to remember:
# http://pubs.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap12.html

from nacl.git import list_git_repositories
from nacl.git import change_or_create_branch
from nacl.git import checkout_branch
from nacl.git import merge_all_repositories
from nacl.git import merge_single_repository
from nacl.git import remote_prune
from nacl.git import remote_diff
from nacl.git import compare_remote
from nacl.base import init_nacl
from vendor.docopt import docopt
import sys
# This is a BAD hack to avoid SSLContext Warnings of urllib3 in python <2.7.9
# See: https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning

if sys.version_info < (2, 7, 9):
    import logging
    logging.captureWarnings(True)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='nacl-git version 0.1')
    # print(arguments)

# Before we do anything else, we check, if nacl will possibly work.
init_nacl()


# list all git repositories
if arguments['list'] or arguments['l']:
    list_git_repositories()

if arguments['branch'] or arguments['b']:
    change_or_create_branch(arguments['BRANCH'])

if arguments['checkout'] or arguments['c']:
    checkout_branch(arguments['BRANCH'])

if arguments['mergeall']:
    merge_all_repositories()

if arguments['merge'] or arguments['m']:
    merge_single_repository()

if arguments['prune'] or arguments['pr']:
    remote_prune()

if arguments['remote-diff'] or arguments['rd']:
    remote_diff()

if arguments['compare-remote'] or arguments['cr']:
    compare_remote()
