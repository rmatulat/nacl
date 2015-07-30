#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ Handels calls to git hoster api like gitlab """

import nacl.fileutils
import nacl.git as ngit
from nacl.helper import color
import sys
import pprint
from vendor.gitlab import Gitlab


class GitLapApiCall(Gitlab):
    """ Api Calls, we are doing based on Gitlab Class"""

    def __init__(self):
        self.config = nacl.fileutils.get_users_nacl_conf()
        super(GitLapApiCall, self).__init__(
            self.config['gitapiserver'],
            token=self.config['gitapitoken']
        )

    def _get_seperator(self):
        """ Get the seperator for splitting up the remote.origin.url """

        # We use the gitapiserver as the value to split the remote origin
        # url, so we can handle origin urls in ssh format as well as in
        # http format
        seperator = self.config['gitapiserver']
        if seperator.startswith('http://'):
            seperator = seperator[7:]
        elif seperator.startswith('https://'):
            seperator = seperator[8:]

        if seperator.endswith('/'):
            seperator = seperator[:-1]
        return seperator

    def get_project_id(self):
        """ returns a gitlab Project ID """
        if not ngit.is_git_repo():
            print(color('WARNING', 'Not a git repository'))
            sys.exit(1)

        seperator = self._get_seperator()

        remote = ngit.git(['config', '--get', 'remote.origin.url'])
        remote = remote.rstrip().split(seperator)[1]

        try:
            return self.getproject(remote[1:-4])['id']
        except:
            print(color('WARNING', 'API Call?'))
            return False

    def get_group_id(self):
        """ Get the ID of our saltstack gitlab group """
        try:
            for group in self.getgroups():
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
        mergerequests = self.getmergerequests(p_id)
        for mergerequest in mergerequests:
            if mergerequest['state'] == 'closed' or \
               mergerequest['state'] == 'merged':
                continue
            if mergerequest['source_branch'] == sourcebranch and \
               mergerequest['target_branch'] == targetbranch:
                return False

        return True

    def is_mergerequest_open(self, mergerequest_id=None):
        """ Check whether a mergerqeust is new """

        if not mergerequest_id:
            raise ValueError("mergerequest_id must be provided")

        mr_details = self.get_mergerequest_details(mergerequest_id)

        try:
            return bool(mr_details['changes']['state'] == 'opened')
        except KeyError:
            return False

    def get_all_issues(self):
        """ Gets all issues of a project """

        p_id = self.get_project_id()
        issues = None
        if p_id:
            issues = self.getprojectissues(p_id)
        else:
            raise TypeError("No Project ID found!")

        return issues

    def get_all_mergerequests(self):
        """ Returns a list of all mergerequests of a project """
        p_id = self.get_project_id()
        return self.getmergerequests(p_id)

    def list_group_members(self):
        """ Return a list with all project users  """
        g_id = self.get_group_id()
        return self.getgroupmembers(g_id)

    def get_my_issues(self):
        """ List all my open issues """
        issues = self.getissues()
        if issues:
            return issues
        else:
            return False

    def edit_issue(self, issue_id=None, **kwargs):
        """ Closes an issue """

        if not issue_id:
            raise ValueError('issue_id must be provided')
        p_id = self.get_project_id()
        return self.editissue(p_id, issue_id, **kwargs)

    def issue_iid_to_uid(self, iid=None):
        """ Takes a iid and gives the uid back.
            This only works inside a project context, where every issue
            has its own id (iid).
            This is mainly a workaround for users when they are used to work
            with the iid (like on the website) """
        if not iid:
            raise ValueError('iid mus be provided')

        all_project_issues = self.get_all_issues()
        if all_project_issues:
            for issue in all_project_issues:
                if int(issue['iid']) == int(iid):
                    return issue['id']
        return False

    def get_mergerequest_details(self, mergerequest_id):
        """ Gets details of a mergerequest """
        values = {}
        p_id = self.get_project_id()
        values['changes'] = self.getmergerequestchanges(
            p_id, mergerequest_id)
        values['comments'] = self.getmergerequestcomments(
            p_id, mergerequest_id)
        return values

    def mr_is_mergeable(self, mergerequest_id=None):
        """ Check whether a mergerequest can be merged without a conflict .
            Workflow:
            1. create a temporary copy of source_branch we like to check if it is mergeable
            2. create a temporary copy of target_branch we like to check against
            3. Try to merge the tmp_target_branch branch into tmp_source_branch
            4. Return whether it is successfull or not
            5. Cleanup tmp_branches
        """
        if not mergerequest_id:
            raise ValueError('mergerequest_id and/or branch must be provided')

        mr_details = self.get_mergerequest_details(mergerequest_id)
        current_branch = ngit.get_current_branch()
        source_branch = mr_details['changes']['source_branch']
        target_branch = mr_details['changes']['target_branch']

        # Checkout the branches
        reverse_stash = False
        if not ngit.branch_is_clean():
            reverse_stash = True
            ngit.git(['stash'])

        ngit.git(['fetch', 'origin'])
        ngit.git(['checkout', '-b', 'tmp_' + source_branch, 'origin/' + source_branch])

        ngit.git(['checkout', '-b', 'tmp_' + target_branch, 'origin/' + target_branch])

        # Try to merge and cleanup
        try:
            ngit.git(['merge', 'tmp_' + target_branch, 'tmp_' + source_branch])
            ngit.git(['checkout', current_branch])
            if reverse_stash:
                ngit.git(['stash', 'apply'])
            ngit.git(['branch', '-D', 'tmp_' + source_branch])
            ngit.git(['branch', '-D', 'tmp_' + target_branch])
            return True
        except:
            ngit.git(['merge', '--abort'])
            ngit.git(['checkout', current_branch])
            if reverse_stash:
                ngit.git(['stash', 'apply'])
            ngit.git(['branch', '-D', 'tmp_' + source_branch])
            ngit.git(['branch', '-D', 'tmp_' + target_branch])
            return False

    def accept_mergerequest(self, mergerequest_id=None):
        if not mergerequest_id:
            raise ValueError('mergerequest_id must be provided')

        p_id = self.get_project_id()
        return self.acceptmergerequest(p_id, mergerequest_id)

    def remote_branch_exists(self, branch=None, p_id=None):
        """ Check if branch exits on remote"""
        if branch:
            try:
                remote_branch = self.getbranch(p_id, branch)
                return bool(remote_branch)
            except:
                return False
        else:
            raise ValueError("branch must be provided")
