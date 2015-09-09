#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
nacl-flow module

All heavy lifting for nacl-flow is done here.
By now flow only interacts with gitlab.

It was intended to be more flexible so that it can operate with github
as well. But there are some major design flaws done while development.
For example there is no proper abstraction of gitlab and github calls (there
is actually no abstraction at all).
"""
import nacl.gitlabapi as api
from nacl.helper import check_string_to_int
from nacl.helper import query_yes_no
import nacl.git as git
from nacl.decorator import log
import pprint


class NaclFlow(object):
    """
    Abstraction of the nacl-flow workflow

    Most functions are decorated with the @log decorator because the results
    have to be displayed to the user interacting with the salt repositories.
    To make functions testable the output is done by @log.
    """

    def __init__(self):
        """
        Initialize the api.

        At some point in time we have to make this more flexible for
        a use with different APIs like the one of github.
        """
        self.api = api.GitLapApiCall()

    @log
    def get_all_issues(self, all=None):
        """
        Get all issues of a project

        If 'all' is not provided just the open issues are returned.
        """

        _ret = []

        try:
            issues = self.api.get_all_issues()
        except TypeError as e:
            _ret.append(('FAIL', 'Project ID not found. Is remote origin a gitlab repo? ({0})'.format(e.message), 1))
            return _ret

        if issues:
            for issue in issues:
                if not all and issue['state'] == 'closed':
                    continue
                _ret.append(('INFO', "TITLE: " + issue['title']))
                _ret.append(('GREEN', "ID: " + str(issue['iid'])))
                _ret.append(('GREEN', "WHAT: " + issue['description']))
                _ret.append(('GREEN', "STATE: " + issue['state']))
                _ret.append(('INFO', "AUTHOR: " + issue['author']['name']))
                if issue['assignee']:
                    _ret.append((
                        'INFO', "ASSIGNEE: " + issue['assignee']['name']))
                _ret.append(('INFO', '-' * 80))
            return _ret
        else:
            return [('INFO', 'No issues found')]

    @log
    def get_my_issues(self, all=None):
        """
        List the callers issues

        As long as 'all' is not set only open issues are shown.
        """
        issues = self.api.get_my_issues()

        _ret = []
        if issues:
            for issue in issues:
                if not all and issue['state'] == 'closed':
                    continue

                project = self.api.getproject(issue['project_id'])

                _ret.append(('INFO', "TITLE: " + issue['title']))
                _ret.append(('GREEN', "ID: " + str(issue['iid'])))
                _ret.append(('GREEN', "URL: " + project['web_url']))
                _ret.append(('BOLD', "REPO: " + project['description']))
                _ret.append(('GREEN', "WHAT: " + issue['description']))
                _ret.append(('GREEN', "STATE: " + issue['state']))
                _ret.append(('INFO', "AUTHOR: " + issue['author']['name']))
                if issue['assignee']:
                    _ret.append((
                        'GREEN', "ASSIGNEE: " + issue['assignee']['name']))
                _ret.append(('INFO', '-' * 80))
            return _ret
        else:
            return [('INFO', 'No issues found')]

    @log
    def edit_issue(self, issue_id=None, do=None):
        """
        Close or reopen an issue

        'do' must be either 'close' or 'reopen'
        """

        _ret = []

        if not check_string_to_int(issue_id):
            _ret.append(('WARNING', "ID must be an integer", 1))
            return _ret

        issue_id = int(issue_id)
        issue_uid = self.api.issue_iid_to_uid(issue_id)
        if not issue_uid:
            _ret.append(('FAIL',
                        "Issue {0} not found".format(issue_id), 1))
            return _ret

        if do == 'close':
            state_event = 'close'
        elif do == 'reopen':
            state_event = 'reopen'
        else:
            raise ValueError('do must be close or reopen')

        try:
            ret_val = self.api.edit_issue(issue_uid, state_event=state_event)
            if ret_val['state'] == 'closed':
                _ret.append(('GREEN', 'Issue {0} closed'.format(issue_id)))
            elif ret_val['state'] == 'reopened':
                _ret.append(('GREEN', 'Issue {0} reopened'.format(issue_id)))
            else:
                _ret.append((
                    'FAIL',
                    'Issue {0} has state: {1}'
                    .format(issue_id, ret_val['state'])))
        except:
            _ret.append(('FAIL', 'Something went wrong'))

        return _ret

    @log
    def write_patch_for_issue(self, issue_id=None):
        """
        Start a patch

        This is intended to be the first step in a process of providing
        a patch.
        Every patch should be written in its own branch. Therefore we
        provide a simple cmd to create a meaningfull named branch related to
        its issue. Thats why the issue id must be provided.
        There some consistency checks around starting a new branch.
        """

        _ret = []

        # first we have to do a few consistency checks
        if not check_string_to_int(issue_id):
            _ret.append(('WARNING', "ID must be an integer", 1))
            return _ret

        issue_id = int(issue_id)

        if not git.is_git_repo():
            _ret.append(('WARNING', "Not a git repository", 1))
            return _ret

        if not git.branch_is_clean():
            _ret.append((
                'WARNING',
                "Your branch is not clean. Please commit your changes first."))
            return _ret

        p_id = self.api.get_project_id()

        # Transform iid to id
        try:
            issue_uid = self.api.issue_iid_to_uid(issue_id)

            issue = self.api.getprojectissue(p_id, issue_uid)
            if not issue:
                _ret.append(('WARNING', "Issue ID not found", 1))
                return _ret

            if issue['project_id'] != p_id:
                _ret.append((
                    'WARNING',
                    "The issue ID does not correspond to the current " +
                    "git repository/project", 1))
                return _ret
        except TypeError as e:
            _ret.append(('FAIL', 'Something went wrong: {0}'. format(e.message)))
            return _ret

        # the workflow itself:
        # 1. create a branch
        # 2. switch to that branch.
        git.change_or_create_branch("issue_" + str(issue_id))
        return _ret

    @log
    def push_patch(self, assignee_id=None, mr_text=None):
        """
        Push the patch and provide a mergerequest

        The main problem is to avoid CONFLICTs while accepting a MR in
        accept_mergerequest().
        To support that we check if origin/master can be merged to our
        issue branch. If not the committer has to solve the conflict first
        before the patch might be submitted.

        Btw we force the committer not to use the master branch of the
        repository because we want to keep it clean as far as possible.

        After the patch is pushed to the remote as a new branch the MR
        will be created.
        """

        _ret = []

        if git.get_current_branch() == "master":
            _ret.append((
                'WARNING',
                "You can not open a mergerequest from your "
                "local master branch.\n"
                "Please switch to your issue branch!", 1))
            return _ret

        if not git.branch_is_clean():
            output = git.git(['status', '-s'])
            _ret.append(('INFO', output))
            _ret.append(('WARNING', "You have uncommitted changes. Please commit them first!", 1))
            return _ret

        # We have to do some validating:
        # 1. Check whether the current commit is already in
        #    the remote master branch
        # 2. If not if we need to push our local changes to the
        #    remote. There might be 3 reasons:
        #   - The source_branch of the mergerequest doesn't exists
        #     on the remote.
        #   - If there is no source_branch, we have to merge
        #     the origin/master into our issue branch to avoid
        #     conflicts on the origin side.
        #   - The source_branch exists but we have new commits for that MR
        #
        #  We now have our local changes at the remote in a seperate branch.
        #  Move on:
        #
        #  3. If there is no MR present, create one.
        #
        #  Pray.

        # Step 1: Check whether the commit exist in the remote master branch
        last_local_sha = git.get_last_commit_sha()
        sha_is_on_remote = git.is_commit_on_remote(last_local_sha)

        if sha_is_on_remote:
            _ret.append((
                'WARNING',
                "Your local commit is already in the remote master "
                "branch.\nAborting!", 1))
            return _ret

        # Step 2: Check whether we have to push our local changes to the remote

        need_push = False

        p_id = self.api.get_project_id()
        sourcebranch = git.get_current_branch()

        _ret.append(('GREEN', 'Branch: {0}'.format(sourcebranch)))

        # First check whether the MR branch exists on the remote
        sourcebranch_on_remote = self.api.remote_branch_exists(
            sourcebranch, p_id)

        if not sourcebranch_on_remote:
            need_push = True
            # We need to merge the origin/master into our issue branch because
            # of avoiding conflicts in the merge workflow on the origin side.
            try:
                _ret.append((
                    'INFO',
                    'Try to rebase origin master into {0}'
                    .format(sourcebranch)))

                git.git(['fetch'])
                git.git(['rebase', 'origin/master'])
            except ValueError as e:
                _ret.append((
                    'FAIL',
                    "Merge into {0} failed: {1}".
                    format(sourcebranch, e.message)))

                git.git(['rebase', '--abort'])
                _ret.append(('INFO', 'Please run \n\ngit pull --rebase\n\nand manually resolve your CONFLICTs.'))
                _ret.append(('INFO', 'Then run\n\ngit add <FILE>\n git rebase --continue'))
                _ret.append(('INFO', 'At least run\n\nnacl-flow cp again', 1))
                return _ret

        else:
            # Second check whether we have un-pushed local commits.
            # We check the local source branch compared to the remote
            # source branch.
            unpushed_commits = git.need_pull_push(
                return_returncode=True,
                local_branch=sourcebranch,
                remote_branch=sourcebranch)
            if unpushed_commits == 2:
                need_push = True

        if need_push:
            _ret.append(('INFO', "Pushing to origin " + sourcebranch))
            git.git(['push', 'origin', sourcebranch])
        else:
            _ret.append(('INFO', "Local and remote are up-to-date."))

        # We are done with pushing commits.
        # Step 3. Creating a MR
        if assignee_id:

            if not check_string_to_int(assignee_id):
                _ret.append(('WARNING', "ID must be an integer", 1))
                return _ret

            assignee_id = int(assignee_id)

        targetbranch = 'master'
        if mr_text:
            title = str(mr_text)
        else:
            title = git.git(['log', '--format=%s', '-n', '1'])
        is_new_mergerequest = self.api.is_mergerequest_new(
            sourcebranch, targetbranch)

        if is_new_mergerequest:
            _ret.append(('GREEN', "Create a new mergerequest"))
            self.api.createmergerequest(
                p_id,
                sourcebranch,
                targetbranch,
                title,
                assignee_id=assignee_id)
        else:
            _ret.append(('INFO', "Mergerequests exists. Skipping"))

        return _ret

    @log
    def list_project_members(self):
        """ Display a list of all projectmembers """

        _ret = []

        members = self.api.list_group_members()
        if members:
            for member in members:
                _ret.append(('INFO', "Name: " + member['name']))
                _ret.append(('GREEN', "ID: " + str(member['id'])))
        else:
            _ret.append(('INFO', 'No project members found'))

        return _ret

    @log
    def list_all_mergerequests(self, all=False):
        """ Display all open mergerequests of a project """

        _ret = []

        mergerequests = self.api.get_all_mergerequests()
        for mergerequest in mergerequests:
            if not all and mergerequest['state'] == 'closed' \
               or not all and mergerequest['state'] == 'merged':
                continue

            _ret.append(('INFO', "TITLE: " + mergerequest['title']))
            _ret.append(('GREEN', "BRANCH: " + mergerequest['source_branch']))
            _ret.append(('GREEN', "STATE: " + mergerequest['state']))

            if mergerequest['assignee']:
                _ret.append((
                    'GREEN',
                    "ASSIGNEE: " + mergerequest['assignee']['name']))
            _ret.append(('GREEN', "ID: " + str(mergerequest['id'])))
            _ret.append(('GREEN', "DATE: " + str(mergerequest['created_at'])))
            _ret.append(('INFO', '-' * 80))
            return _ret
        return _ret

    @log
    def get_mergerequest_details(self, mergerequest_id=None):
        """ Display the details of a mergerequest """
        _ret = []
        values = self.api.get_mergerequest_details(mergerequest_id)
        change = values['changes']
        comments = values['comments']

        if not change:
            _ret.append(('FAIL', "Mergerequest not found", 1))
            return _ret

        _ret.append(('INFO', "TITLE: " + change['title']))
        _ret.append(('GREEN', "AUTHOR: " + change['author']['name']))
        _ret.append(('BOLD', "STATE: " + change['state']))
        _ret.append(('GREEN', "DATE: " + change['created_at']))
        _ret.append(('DARKCYAN', "DIFF:\n"))
        for chg in change['changes']:
            _ret.append(('DARKCYAN', "\n" + chg['diff']))

        _ret.append(('INFO', "COMMENTS:"))
        for comment in comments:
            _ret.append(('GREEN', comment['author']['name'] + ":"))
            _ret.append(('GREEN', comment['note'] + "\n" + "-" * 40))

        return _ret

    @log
    def accept_mergerequest(self, mergerequest_id=None):
        """
        Accept a mergerequest

        That has to have an awful workflow, because we want to ensure
        that the MR may merge and will not cause any CONFLICT's.
        CONFLICT's are not a complete desaster but we like to have the
        author of a patch to be responsible for that and not the one
        who accepts the MR.
        """

        _ret = []

        do_merge = query_yes_no("Should mergerequest {0} be merged?"
                                .format(mergerequest_id),
                                "no")

        if not self.api.is_mergerequest_open(mergerequest_id):
            _ret.append((
                'FAIL',
                "Mergerequest '{0}' already closed? "
                "Is there a mergerequest with this ID?"
                .format(mergerequest_id), 1))

            return _ret

        if do_merge:
            _ret.append(('GREEN', "Start merge"))

            if self.api.mr_is_mergeable(mergerequest_id):
                return_values = self.api.accept_mergerequest(mergerequest_id)
            else:
                _ret.append((
                    'FAIL',
                    "Mergerequest would not merge into origin/master", 1))
                p_id = self.api.get_project_id()
                self.api.addcommenttomergerequest(p_id, mergerequest_id, 'Could not be merged due to CONFLICTs')
                return _ret

            if return_values and return_values['state'] == 'merged':
                _ret.append((
                    'GREEN',
                    "Merge complete. Remove " +
                    return_values['source_branch']))
                git.git(['push', 'origin', '--delete', return_values['source_branch']])
            else:
                _ret.append((
                    'FAIL',
                    "Mergerequest already closed? Is there a mergerequest " +
                    "with this ID? State: {0}".format(return_values['state'])))
        else:
            _ret.append(('INFO', "Merge aborted!"))

        return _ret

    @log
    def get_commit(self, commit=None):
        """ Display a commit """

        _ret = []

        if not commit:
            _ret.append(('FAIL', "Commit SHA must be provided"))
            return _ret

        p_id = self.api.get_project_id()
        details = self.api.getrepositorycommit(p_id, commit)
        diffs = self.api.getrepositorycommitdiff(p_id, commit)

        if details:
            _ret.append(('BOLD', "COMMIT: {0}".format(commit)))
            _ret.append(('GREEN', "AUTHOR: {0}".format(details['author_name'])))
            _ret.append(('GREEN', "MESSAGE:\n{0}".format(details['message'].encode('utf-8'))))
            _ret.append(('GREEN', "DATE: {0}".format(details['created_at'])))
        else:
            _ret.append(('FAIL', "Commit not found: {0}".format(commit), 1))
            return _ret

        if diffs:
            _ret.append(('GREEN', "DIFF:\n"))
            for diff in diffs:
                _ret.append(('BOLD', "\n{0}".format(diff['diff'])))

        return _ret
