#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        self.p_id = self.api.get_project_id()

    @log
    def get_all_issues(self, all=None):
        """
        Get all issues of a project

        If 'all' is not provided just the open issues are returned.
        """

        __ret = []

        try:
            issues = self.api.get_all_issues()
        except TypeError as e:
            __ret.append(('FAIL', 'Project ID not found. Is remote origin a gitlab repo? ({0})'.format(e.message), 1))
            return __ret

        if issues:
            for issue in issues:
                if not all and issue['state'] == 'closed':
                    continue
                __ret.append(('INFO', "TITLE: " + issue['title']))
                __ret.append(('GREEN', "ID: " + str(issue['iid'])))
                __ret.append(('GREEN', "WHAT: " + issue['description']))
                __ret.append(('GREEN', "STATE: " + issue['state']))
                __ret.append(('INFO', "AUTHOR: " + issue['author']['name']))
                if issue['assignee']:
                    __ret.append((
                        'INFO', "ASSIGNEE: " + issue['assignee']['name']))
                __ret.append(('INFO', '-' * 80))
            if not __ret:
                return [('INFO', 'No issues found')]
            return __ret
        else:
            return [('INFO', 'No issues found')]

    @log
    def get_my_issues(self, all=None):
        """
        List the callers issues

        As long as 'all' is not set only open issues are shown.
        """
        issues = self.api.getissues()

        __ret = []

        for issue in issues:
            if not all and issue['state'] == 'closed':
                continue

            project = self.api.getproject(issue['project_id'])

            __ret.append(('INFO', "TITLE: " + issue['title']))
            __ret.append(('GREEN', "ID: " + str(issue['iid'])))
            __ret.append(('GREEN', "URL: " + project['web_url']))
            __ret.append(('BOLD', "REPO: " + project['description']))
            __ret.append(('GREEN', "WHAT: " + issue['description']))
            __ret.append(('GREEN', "STATE: " + issue['state']))
            __ret.append(('INFO', "AUTHOR: " + issue['author']['name']))
            if issue['assignee']:
                __ret.append((
                    'GREEN', "ASSIGNEE: " + issue['assignee']['name']))
            __ret.append(('INFO', '-' * 80))
        if not __ret:
            return [('INFO', 'No open issues found. Try nacl-flow mi all')]
        return __ret

    @log
    def edit_issue(self, issue_id=None, do=None):
        """
        Close or reopen an issue

        'do' must be either 'close' or 'reopen'
        """

        __ret = []

        if not check_string_to_int(issue_id):
            __ret.append(('WARNING', "ID must be an integer", 1))
            return __ret

        issue_id = int(issue_id)
        issue_uid = self.api.issue_iid_to_uid(issue_id)
        if not issue_uid:
            __ret.append(('FAIL',
                        "Issue {0} not found".format(issue_id), 1))
            return __ret

        if do == 'close':
            state_event = 'close'
        elif do == 'reopen':
            state_event = 'reopen'
        else:
            raise ValueError('do must be close or reopen')

        try:
            ret_val = self.api.edit_issue(issue_uid, state_event=state_event)
            if ret_val['state'] == 'closed':
                __ret.append(('GREEN', 'Issue {0} closed'.format(issue_id)))
            elif ret_val['state'] == 'reopened':
                __ret.append(('GREEN', 'Issue {0} reopened'.format(issue_id)))
            else:
                __ret.append((
                    'FAIL',
                    'Issue {0} has state: {1}'
                    .format(issue_id, ret_val['state'])))
        except:
            __ret.append(('FAIL', 'Something went wrong'))

        return __ret

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

        __ret = []

        # first we have to do a few consistency checks
        if not check_string_to_int(issue_id):
            __ret.append(('WARNING', "ID must be an integer", 1))
            return __ret

        issue_id = int(issue_id)

        if not git.is_git_repo():
            __ret.append(('WARNING', "Not a git repository", 1))
            return __ret

        if not git.branch_is_clean():
            __ret.append((
                'WARNING',
                "Your branch is not clean. Please commit your changes first."))
            return __ret

        # Transform iid to id
        try:
            issue_uid = self.api.issue_iid_to_uid(issue_id)

            issue = self.api.getprojectissue(self.p_id, issue_uid)
            if not issue:
                __ret.append(('WARNING', "Issue ID not found", 1))
                return __ret

            if issue['project_id'] != self.p_id:
                __ret.append((
                    'WARNING',
                    "The issue ID does not correspond to the current " +
                    "git repository/project", 1))
                return __ret
        except TypeError as e:
            __ret.append(('FAIL', 'Something went wrong: {0}'. format(e.message)))
            return __ret

        # the workflow itself:
        # 1. create a branch
        # 2. switch to that branch.
        git.change_or_create_branch("issue_" + str(issue_id))
        return __ret

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

        __ret = []

        if git.get_current_branch() == "master":
            __ret.append((
                'WARNING',
                "You can not open a mergerequest from your "
                "local master branch.\n"
                "Please switch to your issue branch!", 1))
            return __ret

        if not git.branch_is_clean():
            output = git.git(['status', '-s'])
            __ret.append(('INFO', output))
            __ret.append(('WARNING', "You have uncommitted changes. Please commit them first!", 1))
            return __ret

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
            __ret.append((
                'WARNING',
                "Your local commit is already in the remote master "
                "branch.\nAborting!", 1))
            return __ret

        # Step 2: Check whether we have to push our local changes to the remote

        need_push = False

        sourcebranch = git.get_current_branch()

        __ret.append(('GREEN', 'Branch: {0}'.format(sourcebranch)))

        # First check whether the MR branch exists on the remote
        sourcebranch_on_remote = self.api.remote_branch_exists(sourcebranch)

        if not sourcebranch_on_remote:
            need_push = True
            # We need to merge the origin/master into our issue branch because
            # of avoiding conflicts in the merge workflow on the origin side.
            try:
                __ret.append((
                    'INFO',
                    'Try to rebase origin master into {0}'
                    .format(sourcebranch)))

                git.git(['fetch'])
                git.git(['rebase', 'origin/master'])
            except ValueError as e:
                __ret.append((
                    'FAIL',
                    "Merge into {0} failed: {1}".
                    format(sourcebranch, e.message)))

                git.git(['rebase', '--abort'])
                __ret.append(('INFO', 'Please run \n\ngit pull --rebase\n\nand manually resolve your CONFLICTs.'))
                __ret.append(('INFO', 'Then run\n\ngit add <FILE>\n git rebase --continue'))
                __ret.append(('INFO', 'At least run\n\nnacl-flow cp again', 1))
                return __ret

        else:
            # Second check whether we have un-pushed local commits.
            # We check the local source branch compared to the remote
            # source branch.
            unpushed_commits = git.need_pull_push(
                return__returncode=True,
                local_branch=sourcebranch,
                remote_branch=sourcebranch)
            if unpushed_commits == 2:
                need_push = True

        if need_push:
            __ret.append(('INFO', "Pushing to origin " + sourcebranch))
            git.git(['push', 'origin', sourcebranch])
        else:
            __ret.append(('INFO', "Local and remote are up-to-date."))

        # We are done with pushing commits.
        # Step 3. Creating a MR
        if assignee_id:

            if not check_string_to_int(assignee_id):
                __ret.append(('WARNING', "ID must be an integer", 1))
                return __ret

            assignee_id = int(assignee_id)

        targetbranch = 'master'
        if mr_text:
            title = str(mr_text)
        else:
            title = git.git(['log', '--format=%s', '-n', '1'])
        is_new_mergerequest = self.api.is_mergerequest_new(
            sourcebranch, targetbranch)

        if is_new_mergerequest:
            __ret.append(('GREEN', "Create a new mergerequest"))

            if not self.api.createmergerequest(
                    self.p_id,
                    sourcebranch,
                    targetbranch,
                    title,
                    assignee_id=assignee_id):
                __ret.append(('FAIL', "Creating Mergerequest failed!"))
        else:
            __ret.append(('INFO', "Mergerequests exists. Skipping"))

        return __ret

    @log
    def list_project_members(self):
        """ Display a list of all projectmembers """

        __ret = []

        members = self.api.list_group_members()
        if members:
            for member in members:
                __ret.append(('INFO', "Name: " + member['name']))
                __ret.append(('GREEN', "ID: " + str(member['id'])))
        else:
            __ret.append(('INFO', 'No project members found'))

        return __ret

    @log
    def list_all_mergerequests(self, all=False):
        """ Display all open mergerequests of a project """

        __ret = []

        mergerequests = self.api.getmergerequests(self.p_id)
        for mergerequest in mergerequests:
            if not all and mergerequest['state'] == 'closed' \
               or not all and mergerequest['state'] == 'merged':
                continue

            __ret.append(('INFO', "TITLE: " + mergerequest['title']))
            __ret.append(('GREEN', "BRANCH: " + mergerequest['source_branch']))
            __ret.append(('GREEN', "STATE: " + mergerequest['state']))

            if mergerequest['assignee']:
                __ret.append((
                    'GREEN',
                    "ASSIGNEE: " + mergerequest['assignee']['name']))
            __ret.append(('GREEN', "ID: " + str(mergerequest['id'])))
            __ret.append(('GREEN', "DATE: " + str(mergerequest['created_at'])))
            __ret.append(('INFO', '-' * 80))
            return __ret
        return __ret

    @log
    def get_mergerequest_details(self, mergerequest_id=None):
        """ Display the details of a mergerequest """
        __ret = []
        values = self.api.get_mergerequest_details(mergerequest_id)
        change = values['changes']
        comments = values['comments']

        if not change:
            __ret.append(('FAIL', "Mergerequest not found", 1))
            return __ret

        __ret.append(('INFO', "TITLE: " + change['title']))
        __ret.append(('GREEN', "AUTHOR: " + change['author']['name']))
        __ret.append(('BOLD', "STATE: " + change['state']))
        __ret.append(('GREEN', "DATE: " + change['created_at']))
        __ret.append(('DARKCYAN', "DIFF:\n"))
        for chg in change['changes']:
            __ret.append(('DARKCYAN', "\n" + chg['diff']))

        __ret.append(('INFO', "COMMENTS:"))
        for comment in comments:
            __ret.append(('GREEN', comment['author']['name'] + ":"))
            __ret.append(('GREEN', comment['note'] + "\n" + "-" * 40))

        return __ret

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

        __ret = []

        do_merge = query_yes_no("Should mergerequest {0} be merged?"
                                .format(mergerequest_id),
                                "no")

        if not self.api.is_mergerequest_open(mergerequest_id):
            __ret.append((
                'FAIL',
                "Mergerequest '{0}' already closed? "
                "Is there a mergerequest with this ID?"
                .format(mergerequest_id), 1))

            return __ret

        if do_merge:
            __ret.append(('GREEN', "Start merge"))

            if self.api.mr_is_mergeable(mergerequest_id):
                return_values = self.api.accept_mergerequest(mergerequest_id)
            else:
                __ret.append((
                    'FAIL',
                    "Mergerequest would not merge into origin/master", 1))

                self.api.addcommenttomergerequest(
                    self.p_id, mergerequest_id,
                    'Could not be merged due to CONFLICTs')
                return __ret

            if return_values and return_values['state'] == 'merged':
                __ret.append((
                    'GREEN',
                    "Merge complete. Remove " +
                    return_values['source_branch']))
                git.git(['push', 'origin', '--delete', return_values['source_branch']])
            else:
                __ret.append((
                    'FAIL',
                    "Mergerequest already closed? Is there a mergerequest " +
                    "with this ID? State: {0}".format(return_values['state'])))
        else:
            __ret.append(('INFO', "Merge aborted!"))

        return __ret

    @log
    def get_commit(self, commit=None):
        """ Display a commit """

        __ret = []

        if not commit:
            __ret.append(('FAIL', "Commit SHA must be provided"))
            return __ret

        details = self.api.getrepositorycommit(self.p_id, commit)
        diffs = self.api.getrepositorycommitdiff(self.p_id, commit)

        if details:
            __ret.append(('BOLD', "COMMIT: {0}".format(commit)))
            __ret.append(('GREEN', "AUTHOR: {0}".format(details['author_name'])))
            __ret.append(('GREEN', "MESSAGE:\n{0}".format(details['message'].encode('utf-8'))))
            __ret.append(('GREEN', "DATE: {0}".format(details['created_at'])))
        else:
            __ret.append(('FAIL', "Commit not found: {0}".format(commit), 1))
            return __ret

        if diffs:
            __ret.append(('GREEN', "DIFF:\n"))
            for diff in diffs:
                __ret.append(('BOLD', "\n{0}".format(diff['diff'])))

        return __ret
