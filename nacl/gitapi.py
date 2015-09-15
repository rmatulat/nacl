#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
An API to gitlab and github instances

WARNING: This module is a complete failure by now.
It is not doing what it was supposed to do.
We have to clean this up and spend some time to either refactor it out
completly or make it useable as an api for nacl.flow so that we can
switch between gitlab and github by using an config attribute.
"""

from nacl.base import get_users_nacl_conf
from nacl.decorator import log
from nacl.helper import clean_up_dict
import vendor.gitlab
import pprint


def get_gitgitlab_handle(host, my_token):
    """ returns a gitlab api handle """
    return vendor.gitlab.Gitlab(host, token=my_token)


@log
def get_remote_url_dict():
    """
    Get a list of all remote repository urls (like from an gitlab instance).

    All repositories have to be organized in a group, so that we have a
    starting point to look at.
    """

    _ret = []

    config = get_users_nacl_conf()

    try:
        ignore_repositories = config['ignore_repositories']
    except:
        ignore_repositories = []

    git = get_gitgitlab_handle(config['gitapiserver'], config['gitapitoken'])

    group_id = None

    try:
        for group in git.getgroups():
            if group['name'] == config['gitgroup']:
                group_id = group['id']
    except:
        # Fix this: be more precise about what
        # fails.
        _ret.append(('FAIL', 'API call failed! Credentials?', 1))
        return _ret

    if group_id:
        ssh_url_dict = {}
        group = git.getgroups(group_id)

        for project in group['projects']:
            ssh_url_dict[project['ssh_url_to_repo']] = project['description']

        return {'payload': clean_up_dict(ssh_url_dict, ignore_repositories)}
    else:
        _ret.append(('FAIL',
                     "Git group not found: %s" % config['gitgroup'],
                     1))
        return _ret
