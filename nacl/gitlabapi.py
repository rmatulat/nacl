#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nacl.base import get_users_nacl_conf
import nacl.git as git
from nacl.helper import color
import sys
import pprint
from vendor.gitlab import Gitlab


class GitLapApiCall(Gitlab):
    """
    Api Calls, we are doing based on Gitlab Class

    It extends Gitlab with some helper functions we need mainly in nacl.flow.
    """

    def __init__(self):
        self.config = get_users_nacl_conf()
        super(GitLapApiCall, self).__init__(
            self.config['gitapiserver'],
            token=self.config['gitapitoken']
        )
        self.p_id = self.get_project_id()

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
        """ Return a gitlab Project ID """

        if not git.is_git_repo():
            print(color('WARNING', 'Not a git repository'))
            sys.exit(1)

        seperator = self._get_seperator()

        remote = git.git(['config', '--get', 'remote.origin.url'])
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

        mergerequests = self.getmergerequests(self.p_id)
        for mergerequest in mergerequests:
            if mergerequest['state'] == 'closed' or \
               mergerequest['state'] == 'merged':
                continue
            if mergerequest['source_branch'] == sourcebranch and \
               mergerequest['target_branch'] == targetbranch:
                return False

        return True

    def is_mergerequest_open(self, mergerequest_id=None):
        """ Check whether a mergerqeust is open """

        if not mergerequest_id:
            raise ValueError("mergerequest_id must be provided")

        mr_details = self.get_mergerequest_details(mergerequest_id)

        try:
            return bool(mr_details['changes']['state'] == 'opened')
        except (KeyError, TypeError):
            return False

    def get_all_issues(self):
        """ Get all issues of a project """

        issues = self.getprojectissues(self.p_id)
        if issues:
            return issues
        else:
            raise TypeError("No Project ID found!")

    def list_group_members(self):
        """ Return a list with all project users  """

        g_id = self.get_group_id()
        return self.getgroupmembers(g_id)

    def edit_issue(self, issue_id=None, **kwargs):
        """ Close an issue """

        if not issue_id:
            raise ValueError('issue_id must be provided')

        return self.editissue(self.p_id, issue_id, **kwargs)

    def issue_iid_to_uid(self, iid=None):
        """
        Convert the iid to the well known uid

        Takes a iid and gives the uid back.
        This only works inside a project context where every issue
        has its own id (iid).
        This is mainly a workaround for users when they are used to work
        with the iid (like shown on the website).
        """
        if not iid:
            raise ValueError('iid mus be provided')

        all_project_issues = self.get_all_issues()
        if all_project_issues:
            for issue in all_project_issues:
                try:
                    if int(issue['iid']) == int(iid):
                        return issue['id']
                except ValueError:
                    return False
        return False

    def mergerequest_iid_to_id(self, iid=None):
        """
        Convert iid to id

        The iid is the number shown to the user in the GUI.
        But behind the scenes there is a id, that is being used instead for
        querying the API. So we have to transform the user-friendly iid
        to an id.
        """
        if not iid:
            raise ValueError('iid mus be provided')

        all_project_mergerequests = self.getmergerequests(self.p_id)
        if all_project_mergerequests:
            for mergerequest in all_project_mergerequests:
                try:
                    if int(mergerequest['iid']) == int(iid):
                        return mergerequest['id']
                except ValueError:
                    return False
        return False

    def get_mergerequest_details(self, mergerequest_id):
        """ Get details of a mergerequest """
        values = {}

        values['changes'] = self.getmergerequestchanges(
            self.p_id, mergerequest_id)
        values['comments'] = self.getmergerequestcomments(
            self.p_id, mergerequest_id)
        return values

    def mr_is_mergeable(self, mergerequest_id=None):
        """
        Is a MR ready to be merged?

        Check whether a mergerequest can be merged without a conflict .
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
        current_branch = git.get_current_branch()
        source_branch = mr_details['changes']['source_branch']
        target_branch = mr_details['changes']['target_branch']

        # Checkout the branches
        reverse_stash = False
        if not git.branch_is_clean():
            reverse_stash = True
            git.git(['stash'])

        git.git(['fetch', 'origin'])
        git.git(['checkout', '-b', 'tmp_' + source_branch, 'origin/' + source_branch])

        git.git(['checkout', '-b', 'tmp_' + target_branch, 'origin/' + target_branch])

        # Try to merge and cleanup
        try:
            git.git(['merge', 'tmp_' + target_branch, 'tmp_' + source_branch])
            git.git(['checkout', current_branch])
            if reverse_stash:
                git.git(['stash', 'apply'])
            git.git(['branch', '-D', 'tmp_' + source_branch])
            git.git(['branch', '-D', 'tmp_' + target_branch])
            return True
        except:
            git.git(['merge', '--abort'])
            git.git(['checkout', current_branch])
            if reverse_stash:
                git.git(['stash', 'apply'])
            git.git(['branch', '-D', 'tmp_' + source_branch])
            git.git(['branch', '-D', 'tmp_' + target_branch])
            return False

    def accept_mergerequest(self, mergerequest_id=None):
        if not mergerequest_id:
            raise ValueError('mergerequest_id must be provided')

        return self.acceptmergerequest(self.p_id, mergerequest_id)

    def remote_branch_exists(self, branch=None):
        """ Check if branch exits on remote """

        if branch:
            try:
                remote_branch = self.getbranch(self.p_id, branch)
                return bool(remote_branch)
            except:
                return False
        else:
            raise ValueError("branch must be provided")
