#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ Handels calls to git hoster api like gitlab """

import nacl.fileutils
import vendor.gitlab
import sys
import pprint


def get_gitgitlab_handle(host, my_token):
    """ returns a gitlab api handle """
    return vendor.gitlab.Gitlab(host, token=my_token)


def clean_up_repositorie(repo_dict, ignore_list):
    """ Cleans up a dict and removes repositories that should be ignored """
    for i in ignore_list:
        repo_dict.pop(i, None)
    return repo_dict


def get_remote_url_dict():
    """
    Get a list of all remote repository url (like from an gitlab instance).
    All repositories have to be organized in a group, so that we have a
    starting point to look at.
    TODO: Make this testable. Currently it's not.
    """

    config = nacl.fileutils.get_users_nacl_conf()

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
        print("[ERROR]: API call failed! Credentials?")
        sys.exit(3)

    if group_id:
        ssh_url_dict = {}
        group = git.getgroups(group_id)

        for project in group['projects']:
            ssh_url_dict[project['ssh_url_to_repo']] = project['description']

        return clean_up_repositorie(ssh_url_dict, ignore_repositories)
    else:
        print("Git group not found: %s" % config['gitgroup'])
        sys.exit(3)

