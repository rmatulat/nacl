#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ Handels calls to git hoster api like gitlab """

import nacl.fileutils
import nacl.git as ngit
from nacl.helper import color
import vendor.gitlab
import sys
import pprint


class GitLapApiCall(object):
    """ Api Calls, we are doing based on Gitlab Class"""

    def __init__(self):
        self.config = nacl.fileutils.get_users_nacl_conf()

        self.git = vendor.gitlab.Gitlab(self.config['gitapiserver'], token=self.config['gitapitoken'])

    def get_project_id(self):
        """ returns a gitlab Project ID """
        if not ngit.is_git_repo():
            print(color('WARNING', 'Not a git repository'))
            sys.exit(1)

        remote = ngit.git(['config', '--get', 'remote.origin.url'])
        remote = remote.rstrip().split(':')[1]
        try:
            return self.git.getproject(remote[:-4])['id']
        except:
            print(color('WARNING', 'API Call?'))
            return False

    def get_group_id(self):
        """ Get the ID of our saltstack gitlab group """
        try:
            for group in self.git.getgroups():
                if group['name'] == self.config['gitgroup']:
                    return group['id']
        except:
            print(color('WARNING', 'API Call?'))
            return False

    def is_mergerequest_new(self, sourcebranch=None, targetbranch=None):
        """ Check whether a mergerqeust is new """

        if not sourcebranch or not targetbranch:
            raise ValueError("sourcebranch and targetbranch must be provided")

        p_id = self.get_project_id()
        mergerequests = self.git.getmergerequests(p_id)
        for mergerequest in mergerequests:
            if mergerequest['state'] == 'closed' or mergerequest['state'] == 'merged':
                continue
            if mergerequest['source_branch'] == sourcebranch and mergerequest['target_branch'] == targetbranch:
                return False

        return True

    def get_all_issues(self):
        """ Gets all issues of a project """
        p_id = self.get_project_id()
        issues = None
        if p_id:
            issues = self.git.getprojectissues(p_id)
        else:
            raise TypeError("No Project ID found!")

        return issues

    def get_all_mergerequests(self):
        """ Returns a list of all mergerequests of a project """
        p_id = self.get_project_id()
        return self.git.getmergerequests(p_id)

    def list_group_members(self):
        """ Return a list with all project users  """
        g_id = self.get_group_id()
        return self.git.getgroupmembers(g_id)

    def get_my_issues(self):
        """ List all my open issues """
        issues = self.git.getissues()
        if issues:
            return issues
        else:
            return False

    def issue_iid_to_uid(self, iid=None):
        """ Takes a iid and gives the uid back.
            This only works inside a project context, where every issue
            has its own id (iid).
            This is mainly a workaround for users where they are used to work
            with the iid (like on the website) """
        if not iid:
            raise ValueError('iid mus be provided')

        all_project_issues = self.get_all_issues()
        if all_project_issues:
            for issue in all_project_issues:
                if issue['iid'] == iid:
                    return issue['id']
        return False

    def get_mergerequest_details(self, mergerequest_id):
        """ Gets details of a mergerequest """
        values = {}
        p_id = self.get_project_id()
        values['changes'] = self.git.getmergerequestchanges(p_id, mergerequest_id)
        values['comments'] = self.git.getmergerequestcomments(p_id, mergerequest_id)
        return values

    def accept_mergerequest(self, mergerequest_id):
        p_id = self.get_project_id()
        return self.git.acceptmergerequest(p_id, mergerequest_id)

    def remote_branch_exists(self, branch, p_id):
        """ Check if branch exits on remote"""
        if branch:
            try:
                remote_branch = self.git.getbranch(p_id, branch)
                return bool(remote_branch)
            except:
                return False
        else:
            raise ValueError("branch must be provided")

    # This is shit.
    # I have to fix this an inherit from Gitlab
    def getproject(self, id):
        return self.git.getproject(id)

    def getprojectissue(self, p_id, issue_id):
        return self.git.getprojectissue(p_id, issue_id)

    def createmergerequest(self, p_id, sourcebranch, targetbranch, title, assignee_id=None):
        return self.git.createmergerequest(p_id, sourcebranch, targetbranch, title, assignee_id=assignee_id)

    def updatemergerequest(self, p_id, mergerequest_id, **kwargs):
        return self.git.updatemergerequest(p_id, mergerequest_id, **kwargs)

    def getbranch(self, p_id, branch):
        return self.git.getbranch(p_id, branch)
    # Shit ends here
