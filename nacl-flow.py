#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""nacl-flow

Usage:
  nacl-flow.py (issues | i) [all]
  nacl-flow.py (my-issues | mi) [all]
  nacl-flow.py (close-issue | ci) ID
  nacl-flow.py (reopen-issue | roi) ID
  nacl-flow.py (projectmember | pm)
  nacl-flow.py (mergerequests | mr) [all]
  nacl-flow.py (mergedetails | md) MERGEREQUEST_ID
  nacl-flow.py (accept-merge | am) MERGEREQUEST_ID
  nacl-flow.py (start-patch | sp) ID
  nacl-flow.py (commit-patch | cp) [ASSIGNEE] [TEXT]
  nacl-flow.py (-h | --help)
  nacl-flow.py --version

Options:
  issues            List all open issues (all = plus closed ones )
  my-issues         List all my open issues (all = plus closed ones )
  close-issue       Closes an issue
  reopen-issue      Reopen an issue
  projectmember     List all possible assignees
  mergerequests     List all open mergerequests of a project
  mergedetails      Show details of a mergerequest
  start-patch       Step 1 in resolving an issue: start a patch. NOTE: You have to provide the ID of the issue
  commit-patch      Step 2 open a mergerequest, ASSIGNEE = ID of a user, TEXT = MR text
  acceptmerge       Accept a mergerequest
  -h --help         Show this screen.
  --version         Show version.

"""

from nacl.flow import NaclFlow
from nacl.base import init_nacl
from vendor.docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='nacl-flow version 0.1')
    # print(arguments)

# Before we do anything else, we check, if nacl will possibly work.
init_nacl()

if arguments['issues'] or arguments['i']:
    flow = NaclFlow()
    flow.get_all_issues(arguments['all'])

if arguments['my-issues'] or arguments['mi']:
    flow = NaclFlow()
    flow.get_my_issues(arguments['all'])

if arguments['close-issue'] or arguments['ci']:
    flow = NaclFlow()
    flow.edit_issue(arguments['ID'], 'close')

if arguments['reopen-issue'] or arguments['roi']:
    flow = NaclFlow()
    flow.edit_issue(arguments['ID'], 'reopen')

if arguments['projectmember'] or arguments['pm']:
    flow = NaclFlow()
    flow.list_project_members()

if arguments['mergerequests'] or arguments['mr']:
    flow = NaclFlow()
    flow.list_all_mergerequests(arguments['all'])

if arguments['mergedetails'] or arguments['md']:
    flow = NaclFlow()
    flow.get_mergerequest_details(arguments['MERGEREQUEST_ID'])

if arguments['accept-merge'] or arguments['am']:
    flow = NaclFlow()
    flow.accept_mergerequest(arguments['MERGEREQUEST_ID'])

if arguments['start-patch'] or arguments['sp']:
    flow = NaclFlow()
    flow.write_patch_for_issue(arguments['ID'])

if arguments['commit-patch'] or arguments['cp']:
    flow = NaclFlow()
    flow.commit_patch(assignee_id=arguments['ASSIGNEE'], mr_text=arguments['TEXT'])
