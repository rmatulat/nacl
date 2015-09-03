#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Test the flow.py """

import unittest
import mock
import pprint
from nacl.flow import NaclFlow


class TestNaclFlow(unittest.TestCase):
    """ Testting the nacl-flow.py main components """

    def setUp(self):
        self.flow = NaclFlow()

    def raise_TypeError():
        raise TypeError('foo')

    # get_all_issues()
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_issues',
                side_effect=raise_TypeError)
    @mock.patch('sys.exit', return_value=None)
    def test_get_all_issues_raises(self, mock, mock_sysexit):
        self.assertEqual(
            [('FAIL', 'Project ID not found. Is remote origin a gitlab repo? (foo)', 1)],
            self.flow.get_all_issues._fn(self.flow))

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_issues',
                return_value=None)
    def test_get_all_issues_no_issues(self, mock):
        self.assertEqual(
            [('INFO', 'No issues found')],
            self.flow.get_all_issues._fn(self.flow))

    # some fake issues

    issues_open = [{
        'state': 'open',
        'project_id': 123,
        'title': 'foo',
        'iid': 123,
        'description': 'baz',
        'author': {'name': 'john doe'},
        'assignee': None
    }]

    issues_closed = [{
        'state': 'closed',
        'project_id': 123,
        'title': 'foo',
        'iid': 123,
        'description': 'baz',
        'author': {'name': 'john doe'},
        'assignee': None
    }]

    issues_assignee = [{
        'state': 'open',
        'project_id': 123,
        'title': 'foo',
        'iid': 123,
        'description': 'baz',
        'author': {'name': 'john doe'},
        u'assignee': {u'name': 'jane doe'}
    }]

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_issues',
                return_value=issues_open)
    def test_get_all_issues_issue_open(self, mock):
        self.assertEqual(
            [('INFO', 'TITLE: foo'),
             ('GREEN', 'ID: 123'),
             ('GREEN', 'WHAT: baz'),
             ('GREEN', 'STATE: open'),
             ('INFO', 'AUTHOR: john doe'),
             ('INFO', '--------------------------------------------------------------------------------')],
            self.flow.get_all_issues._fn(self.flow))

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_issues',
                return_value=issues_closed)
    def test_get_all_issues_issue_closed(self, mock):
        self.assertEqual([], self.flow.get_all_issues._fn(self.flow))

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_issues',
                return_value=issues_assignee)
    def test_get_all_issues_issue_assingnee(self, mock):
        self.assertEqual(
            [('INFO', 'TITLE: foo'),
             ('GREEN', 'ID: 123'),
             ('GREEN', 'WHAT: baz'),
             ('GREEN', 'STATE: open'),
             ('INFO', 'AUTHOR: john doe'),
             ('INFO', 'ASSIGNEE: jane doe'),
             ('INFO', '--------------------------------------------------------------------------------')],
            self.flow.get_all_issues._fn(self.flow))

    # project examples
    project_a = {'web_url': 'http://foo.com',
                 'description': 'foo project'}

    # get_my_issues()

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_my_issues',
                return_value=issues_assignee)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getproject',
                return_value=project_a)
    def test_get_my_issues(self, mock_gai, mock_gp):
        self.assertEquals([('INFO', 'TITLE: foo'),
                           ('GREEN', 'ID: 123'),
                           ('GREEN', 'URL: http://foo.com'),
                           ('BOLD', 'REPO: foo project'),
                           ('GREEN', 'WHAT: baz'),
                           ('GREEN', 'STATE: open'),
                           ('INFO', 'AUTHOR: john doe'),
                           ('GREEN', 'ASSIGNEE: jane doe'),
                           ('INFO',
                            '--------------------------------------------------------------------------------')],
                          self.flow.get_my_issues._fn(self.flow))

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_my_issues',
                return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getproject',
                return_value=project_a)
    def test_get_my_no_issues(self, mock_gai, mock_gp):
        self.assertEquals([('INFO', 'No issues found')],
                          self.flow.get_my_issues._fn(self.flow))

    # edit_issue()

    # test that a non int is provided
    def test_edit_issue_non_int(self):
        self.assertEquals([('WARNING', 'ID must be an integer', 1)],
                          self.flow.edit_issue._fn(self.flow, issue_id='foo'))

    # no issue found
    @mock.patch('nacl.gitlabapi.GitLapApiCall.issue_iid_to_uid',
                return_value=None)
    def test_edit_issue_nf(self, mock):
        self.assertEquals([('FAIL', 'Issue 1 not found', 1)],
                          self.flow.edit_issue._fn(self.flow, issue_id=1))

    @mock.patch('nacl.gitlabapi.GitLapApiCall.issue_iid_to_uid',
                return_value=987)
    def test_edit_issue_raises(self, mock):
        self.assertRaises(ValueError,
                          lambda: self.flow.edit_issue._fn(
                              self.flow,
                              issue_id=1))

    # issue closed
    @mock.patch('nacl.gitlabapi.GitLapApiCall.issue_iid_to_uid',
                return_value=987)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.edit_issue',
                return_value={'state': 'closed'})
    def test_edit_issue_close(self, mock_iid, mock_ei):
        self.assertEquals([('GREEN', 'Issue 1 closed')],
                          self.flow.edit_issue._fn(
                              self.flow,
                              issue_id=1,
                              do='close'))

    # issue reopened
    @mock.patch('nacl.gitlabapi.GitLapApiCall.issue_iid_to_uid',
                return_value=987)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.edit_issue',
                return_value={'state': 'reopened'})
    def test_edit_issue_reopened(self, mock_iid, mock_ei):
        self.assertEquals([('GREEN', 'Issue 1 reopened')],
                          self.flow.edit_issue._fn(
                              self.flow,
                              issue_id=1,
                              do='reopen'))

    # custom ret_val from edit_issue
    @mock.patch('nacl.gitlabapi.GitLapApiCall.issue_iid_to_uid',
                return_value=987)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.edit_issue',
                return_value={'state': 'foo'})
    def test_edit_issue_custom_issue(self, mock_iid, mock_ei):
        self.assertEquals([('FAIL', 'Issue 1 has state: foo')],
                          self.flow.edit_issue._fn(
                              self.flow,
                              issue_id=1,
                              do='reopen'))

    # edit_issue returns None
    @mock.patch('nacl.gitlabapi.GitLapApiCall.issue_iid_to_uid',
                return_value=987)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.edit_issue',
                return_value=None)
    def test_edit_issue_none(self, mock_iid, mock_ei):
        self.assertEquals([('FAIL', 'Something went wrong')],
                          self.flow.edit_issue._fn(
                              self.flow,
                              issue_id=1,
                              do='reopen'))

    # write_patch_for_issue()

    # int must be provided
    @mock.patch('nacl.git.change_or_create_branch', return_value=None)
    def test_write_patch_for_issue_is_int(self, mock_change_or_create):
        self.assertEquals([('WARNING', 'ID must be an integer', 1)],
                          self.flow.write_patch_for_issue._fn(self.flow, issue_id='foo'))

    # no git repo
    @mock.patch('nacl.git.change_or_create_branch', return_value=None)
    @mock.patch('nacl.git.is_git_repo', return_value=False)
    def test_write_patch_for_issue_no_git(self,
                                          mock_change_or_create,
                                          mock_is_git_repo):
        self.assertEquals([('WARNING', 'Not a git repository', 1)],
                          self.flow.write_patch_for_issue._fn(self.flow, issue_id=123))

    # branch is not clean
    @mock.patch('nacl.git.change_or_create_branch', return_value=None)
    @mock.patch('nacl.git.is_git_repo', return_value=True)
    @mock.patch('nacl.git.branch_is_clean', return_value=False)
    def test_write_patch_for_issue_branch_unclean(self,
                                                  mock_change_or_create,
                                                  mock_is_git_repo,
                                                  mock_branch):
        self.assertEquals([('WARNING', 'Your branch is not clean. Please commit your changes first.')],
                          self.flow.write_patch_for_issue._fn(self.flow, issue_id=123))

    def type_error():
        raise ValueError

    # issue id not found
    @mock.patch('nacl.git.change_or_create_branch', return_value=None)
    @mock.patch('nacl.git.is_git_repo', return_value=True)
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.issue_iid_to_uid',
                return_value=987)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getprojectissue',
                return_value=None)
    def test_write_patch_for_issue_not_found(self,
                                             mock_change_or_create,
                                             mock_is_git_repo,
                                             mock_branch,
                                             mock_get_pid,
                                             mock_iid,
                                             mock_getpi):
        self.assertEquals([('WARNING', 'Issue ID not found', 1)],
                          self.flow.write_patch_for_issue._fn(self.flow, issue_id=123))

    sample_issue = {'project_id': 222}

    # issues project id and pid differ
    @mock.patch('nacl.git.change_or_create_branch', return_value=None)
    @mock.patch('nacl.git.is_git_repo', return_value=True)
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.issue_iid_to_uid',
                return_value=987)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getprojectissue',
                return_value=sample_issue)
    def test_write_patch_for_pid_differ(self,
                                        mock_change_or_create,
                                        mock_is_git_repo,
                                        mock_branch,
                                        mock_get_pid,
                                        mock_iid,
                                        mock_getpi):
        self.assertEquals([('WARNING',
                          'The issue ID does not correspond to the current git repository/project',
                           1)],
                          self.flow.write_patch_for_issue._fn(self.flow, issue_id=123))

    # something went wrong
    @mock.patch('nacl.git.change_or_create_branch', return_value=None)
    @mock.patch('nacl.git.is_git_repo', return_value=True)
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.issue_iid_to_uid',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getprojectissue',
                return_value=TypeError('foo'))
    def test_write_patch_something_wrong(self,
                                         mock_change_or_create,
                                         mock_is_git_repo,
                                         mock_branch,
                                         mock_get_pid,
                                         mock_iid,
                                         mock_getpi):
        self.assertEquals([('FAIL', "Something went wrong: sequence index must be integer, not 'str'")],
                          self.flow.write_patch_for_issue._fn(self.flow, issue_id=123))

    # commit_patch()

    # current branch == master
    @mock.patch('nacl.git.get_current_branch', return_value='master')
    def test_commit_patch_not_master_branch(self, mock):
        self.assertEquals([('WARNING',
                            'You can not open a mergerequest from your local master branch.\nPlease switch to your issue branch!',
                            1)], self.flow.commit_patch._fn(self.flow))

    # branch not clean
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=False)
    @mock.patch('nacl.git.git', return_value='bar')
    def test_commit_patch_branch_unclean(self, mock_gcb, mock_bic, mock_git):
        self.assertEquals([('INFO', 'bar'),
                           ('WARNING', 'You have uncommitted changes. Please commit them first!',
                            1)], self.flow.commit_patch._fn(self.flow))

    # Test step 1: Check whether the commit exist in the remote master branch

    # sha is on remote master
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.get_last_commit_sha', return_value='aabbcc')
    @mock.patch('nacl.git.is_commit_on_remote', return_value=True)
    def test_commit_patch_sha_on_remote(self,
                                        mock_gcb,
                                        mock_bic,
                                        mock_glc,
                                        mock_icor):
        self.assertEquals([('WARNING',
                            'Your local commit is already in the remote master branch.\nAborting!',
                            1)], self.flow.commit_patch._fn(self.flow))

    # Test step 2: Check whether we have to push our local
    # changes to the remote

    # source branch not on remote
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.get_last_commit_sha', return_value='aabbcc')
    @mock.patch('nacl.git.is_commit_on_remote', return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.remote_branch_exists',
                return_value=False)
    @mock.patch('nacl.git.git', return_value='dummy')
    @mock.patch('nacl.git.need_pull_push', return_value=0)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_new',
                return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.createmergerequest',
                return_value=True)
    def test_commit_patch_source_branch_not_on_remote(self,
                                                      mock_gcb,
                                                      mock_bic,
                                                      mock_glc,
                                                      mock_icor,
                                                      mock_gpid,
                                                      mock_rbe,
                                                      mock_git,
                                                      mock_npp,
                                                      mock_mrn,
                                                      mock_cmr):
        self.assertEquals([('GREEN', 'Branch: foo'),
                           ('INFO', 'Try to rebase origin master into foo'),
                           ('INFO', 'Pushing to origin foo'),
                           ('GREEN', 'Create a new mergerequest')], self.flow.commit_patch._fn(self.flow))

    # source branch is on remote and local and remote are up to date
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.get_last_commit_sha', return_value='aabbcc')
    @mock.patch('nacl.git.is_commit_on_remote', return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.remote_branch_exists',
                return_value=True)
    @mock.patch('nacl.git.git', return_value='dummy')
    @mock.patch('nacl.git.need_pull_push', return_value=0)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_new',
                return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.createmergerequest',
                return_value=True)
    def test_commit_patch_source_branch_is_on_remote(self,
                                                     mock_gcb,
                                                     mock_bic,
                                                     mock_glc,
                                                     mock_icor,
                                                     mock_gpid,
                                                     mock_rbe,
                                                     mock_git,
                                                     mock_npp,
                                                     mock_mrn,
                                                     mock_cmr):
        self.assertEquals([('GREEN', 'Branch: foo'),
                           ('INFO', 'Local and remote are up-to-date.'),
                           ('GREEN', 'Create a new mergerequest')], self.flow.commit_patch._fn(self.flow))

    # source branch is on remote and we need to push
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.get_last_commit_sha', return_value='aabbcc')
    @mock.patch('nacl.git.is_commit_on_remote', return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.remote_branch_exists',
                return_value=True)
    @mock.patch('nacl.git.git', return_value='dummy')
    @mock.patch('nacl.git.need_pull_push', return_value=2)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_new',
                return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.createmergerequest',
                return_value=True)
    def test_commit_patch_source_branch_is_on_remote_npp(self,
                                                         mock_gcb,
                                                         mock_bic,
                                                         mock_glc,
                                                         mock_icor,
                                                         mock_gpid,
                                                         mock_rbe,
                                                         mock_git,
                                                         mock_npp,
                                                         mock_mrn,
                                                         mock_cmr):
        self.assertEquals([('GREEN', 'Branch: foo'),
                           ('INFO', 'Pushing to origin foo'),
                           ('GREEN', 'Create a new mergerequest')], self.flow.commit_patch._fn(self.flow))

    # Mergerequests exists
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.get_last_commit_sha', return_value='aabbcc')
    @mock.patch('nacl.git.is_commit_on_remote', return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.remote_branch_exists',
                return_value=True)
    @mock.patch('nacl.git.git', return_value='dummy')
    @mock.patch('nacl.git.need_pull_push', return_value=2)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_new',
                return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.createmergerequest',
                return_value=True)
    def test_commit_patch_mergerequest_exists(self,
                                              mock_gcb,
                                              mock_bic,
                                              mock_glc,
                                              mock_icor,
                                              mock_gpid,
                                              mock_rbe,
                                              mock_git,
                                              mock_npp,
                                              mock_mrn,
                                              mock_cmr):
        self.assertEquals([('GREEN', 'Branch: foo'),
                           ('INFO', 'Pushing to origin foo'),
                           ('INFO', 'Mergerequests exists. Skipping')], self.flow.commit_patch._fn(self.flow))

    # We need this helper_func to fake a failed nacl.git.git() call
    def git_sideeffect(args):
        if args == ['fetch']:
            raise ValueError
        else:
            pass

    # git raises an ValueError due to git fails with rebase
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.get_last_commit_sha', return_value='aabbcc')
    @mock.patch('nacl.git.is_commit_on_remote', return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.remote_branch_exists',
                return_value=False)
    @mock.patch('nacl.git.git', side_effect=git_sideeffect)
    @mock.patch('nacl.git.need_pull_push', return_value=2)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_new',
                return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.createmergerequest',
                return_value=True)
    def test_commit_patch_rebase_fails_and_raises(self,
                                                  mock_gcb,
                                                  mock_bic,
                                                  mock_glc,
                                                  mock_icor,
                                                  mock_gpid,
                                                  mock_rbe,
                                                  mock_git,
                                                  mock_npp,
                                                  mock_mrn,
                                                  mock_cmr):
        self.assertEquals([('GREEN', 'Branch: foo'),
                           ('INFO', 'Try to rebase origin master into foo'),
                           ('FAIL', 'Merge into foo failed: '),
                           ('INFO',
                            'Please run \n\ngit pull --rebase\n\nand manually resolve your CONFLICTs.'),
                           ('INFO', 'Then run\n\ngit add <FILE>\n git rebase --continue'),
                           ('INFO', 'At least run\n\nnacl-flow cp again', 1)], self.flow.commit_patch._fn(self.flow))

    # source branch is on remote and we need to push
    # with assignee_id and mr_text provided
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.get_last_commit_sha', return_value='aabbcc')
    @mock.patch('nacl.git.is_commit_on_remote', return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.remote_branch_exists',
                return_value=True)
    @mock.patch('nacl.git.git', return_value='dummy')
    @mock.patch('nacl.git.need_pull_push', return_value=2)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_new',
                return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.createmergerequest',
                return_value=True)
    def test_commit_patch_assignee_id_and_mr_text(self,
                                                  mock_gcb,
                                                  mock_bic,
                                                  mock_glc,
                                                  mock_icor,
                                                  mock_gpid,
                                                  mock_rbe,
                                                  mock_git,
                                                  mock_npp,
                                                  mock_mrn,
                                                  mock_cmr):
        self.assertEquals([('GREEN', 'Branch: foo'),
                           ('INFO', 'Pushing to origin foo'),
                           ('GREEN', 'Create a new mergerequest')],
                          self.flow.commit_patch._fn(
                              self.flow,
                              assignee_id=1,
                              mr_text='baz'))

    # source branch is on remote and we need to push
    # with assignee_id and mr_text provided
    # but assignee_id is crap
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.get_last_commit_sha', return_value='aabbcc')
    @mock.patch('nacl.git.is_commit_on_remote', return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.remote_branch_exists',
                return_value=True)
    @mock.patch('nacl.git.git', return_value='dummy')
    @mock.patch('nacl.git.need_pull_push', return_value=2)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_new',
                return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.createmergerequest',
                return_value=True)
    def test_commit_patch_assignee_id_is_no_int(self,
                                                mock_gcb,
                                                mock_bic,
                                                mock_glc,
                                                mock_icor,
                                                mock_gpid,
                                                mock_rbe,
                                                mock_git,
                                                mock_npp,
                                                mock_mrn,
                                                mock_cmr):
        self.assertEquals([('GREEN', 'Branch: foo'),
                           ('INFO', 'Pushing to origin foo'),
                           ('WARNING', 'ID must be an integer', 1)],
                          self.flow.commit_patch._fn(
                              self.flow,
                              assignee_id='a',
                              mr_text='baz'))

    # list_project_members()

    @mock.patch('nacl.gitlabapi.GitLapApiCall.list_group_members',
                return_value=[{'name': 'foo', 'id': 1}])
    def test_list_group_members_member_found(self, mock):
        self.assertEquals([('INFO', 'Name: foo'), ('GREEN', 'ID: 1')],
                          self.flow.list_project_members._fn(self.flow))

    @mock.patch('nacl.gitlabapi.GitLapApiCall.list_group_members',
                return_value=None)
    def test_list_group_members_no_member_found(self, mock):
        self.assertEquals([('INFO', 'No project members found')],
                          self.flow.list_project_members._fn(self.flow))

    sample_mr_open_list = [{
        'state': 'open',
        'title': 'foo_title',
        'assignee': {'name': 'Jane Doe'},
        'source_branch': 'foo_branch',
        'id': 123,
        'created_at': 'foo_date'}]

    sample_mr_closed_list = [{
        'state': 'closed',
        'title': 'foo_title',
        'assignee': {'name': 'Jane Doe'},
        'source_branch': 'foo_branch',
        'id': 123,
        'created_at': 'foo_date'}]

    # list_all_mergerequests()

    # Only opened MR
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_mergerequests',
                return_value=sample_mr_open_list)
    def test_list_all_mergerequests(self, mock):
        self.assertEquals([('INFO', 'TITLE: foo_title'),
                           ('GREEN', 'BRANCH: foo_branch'),
                           ('GREEN', 'STATE: open'),
                           ('GREEN', 'ASSIGNEE: Jane Doe'),
                           ('GREEN', 'ID: 123'),
                           ('GREEN', 'DATE: foo_date'),
                           ('INFO',
                            '--------------------------------------------------------------------------------')],
                          self.flow.list_all_mergerequests._fn(self.flow))

    # List closed MR
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_mergerequests',
                return_value=sample_mr_closed_list)
    def test_list_all_mergerequests_list_closed(self, mock):
        self.assertEquals([('INFO', 'TITLE: foo_title'),
                           ('GREEN', 'BRANCH: foo_branch'),
                           ('GREEN', 'STATE: closed'),
                           ('GREEN', 'ASSIGNEE: Jane Doe'),
                           ('GREEN', 'ID: 123'),
                           ('GREEN', 'DATE: foo_date'),
                           ('INFO',
                            '--------------------------------------------------------------------------------')],
                          self.flow.list_all_mergerequests._fn(self.flow, all='all'))

    # Closed MR (return of an empty list)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_mergerequests',
                return_value=sample_mr_closed_list)
    def test_list_all_mergerequests_closed(self, mock):
        self.assertEquals([], self.flow.list_all_mergerequests._fn(self.flow))

    # get_mergerequest_details()

    sample_mr_open = {
        'changes': {
            'title': 'foo_title',
            'author': {'name': 'Jane Doe'},
            'state': 'merged',
            'created_at': 'foo_date',
            'changes': [{'diff': 'foo_diff'}]
        },
        'comments': [{
            'author': {'name': 'John Doe'},
            'note': 'foo_note'
        }]
    }

    sample_mr_not_found = {
        'changes': {},
        'comments': [{
            'author': {'name': 'John Doe'},
            'note': 'foo_note'
        }]
    }

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_mergerequest_details',
                return_value=sample_mr_open)
    def test_get_mergerequest_details(self, mock):
        self.assertEquals([('INFO', 'TITLE: foo_title'),
                           ('GREEN', 'AUTHOR: Jane Doe'),
                           ('BOLD', 'STATE: merged'),
                           ('GREEN', 'DATE: foo_date'),
                           ('DARKCYAN', 'DIFF:\n'),
                           ('DARKCYAN', '\nfoo_diff'),
                           ('INFO', 'COMMENTS:'),
                           ('GREEN', 'John Doe:'),
                           ('GREEN', 'foo_note\n----------------------------------------')],
                          self.flow.get_mergerequest_details._fn(self.flow))

    # MR not found
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_mergerequest_details',
                return_value=sample_mr_not_found)
    def test_get_mergerequest__mr_not_found(self, mock):
        self.assertEquals([('FAIL', 'Mergerequest not found', 1)],
                          self.flow.get_mergerequest_details._fn(self.flow))

    # accept_mergerequest()

    # MR is already closed
    @mock.patch('nacl.flow.query_yes_no', return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_open',
                return_value=False)
    def test_accept_mergerequest_mr_closed(self, mock_yn, mock_imro):
        self.assertEquals([('FAIL',
                            "Mergerequest 'None' already closed? Is there a mergerequest with this ID?",
                            1)], self.flow.accept_mergerequest._fn(self.flow))

    # Merge aborted
    @mock.patch('nacl.flow.query_yes_no', return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_open',
                return_value=True)
    def test_accept_mergerequest_aborted(self, mock_yn, mock_imro):
        self.assertEquals([('INFO', 'Merge aborted!')], self.flow.accept_mergerequest._fn(self.flow))

    sample_ret_value = {
        'state': 'merged',
        'source_branch': 'foo'
    }

    sample_ret_value_not_merged = {
        'state': '_not_merged',
        'source_branch': 'foo'
    }

    # Normal, perfect workflow
    @mock.patch('nacl.flow.query_yes_no', return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_open',
                return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.mr_is_mergeable',
                return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.accept_mergerequest',
                return_value=sample_ret_value)
    @mock.patch('nacl.git.git', return_value=None)
    def test_accept_mergerequest_workflow(self,
                                          mock_yn,
                                          mock_imro,
                                          mock_mim,
                                          mock_amr,
                                          mock_git):
        self.assertEquals([('GREEN', 'Start merge'),
                           ('GREEN', 'Merge complete. Remove foo')],
                          self.flow.accept_mergerequest._fn(self.flow))

    # MR not mergeable
    @mock.patch('nacl.flow.query_yes_no', return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_open',
                return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.mr_is_mergeable',
                return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.accept_mergerequest',
                return_value=sample_ret_value)
    @mock.patch('nacl.git.git', return_value=None)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.addcommenttomergerequest',
                return_value=None)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    def test_accept_mergerequest_not_mergeable(self,
                                               mock_yn,
                                               mock_imro,
                                               mock_mim,
                                               mock_amr,
                                               mock_git,
                                               mock_actmr,
                                               mock_gpid):
        self.assertEquals([('GREEN', 'Start merge'),
                           ('FAIL', 'Mergerequest would not merge into origin/master', 1)],
                          self.flow.accept_mergerequest._fn(self.flow))

    # For some reason the MR was not merged
    @mock.patch('nacl.flow.query_yes_no', return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.is_mergerequest_open',
                return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.mr_is_mergeable',
                return_value=True)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.accept_mergerequest',
                return_value=sample_ret_value_not_merged)
    @mock.patch('nacl.git.git', return_value=None)
    def test_accept_mergerequest_not_merged(self,
                                            mock_yn,
                                            mock_imro,
                                            mock_mim,
                                            mock_amr,
                                            mock_git):
        self.assertEquals([('GREEN', 'Start merge'),
                           ('FAIL',
                            'Mergerequest already closed? Is there a mergerequest with this ID? State: _not_merged')],
                          self.flow.accept_mergerequest._fn(self.flow))

    # get_commit()

    def test_get_commit_missing_sha(self):
        self.assertEquals([('FAIL', 'Commit SHA must be provided')], self.flow.get_commit._fn(self.flow))

    # Commit not found
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getrepositorycommit',
                return_value=False)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getrepositorycommitdiff',
                return_value=False)
    def test_get_commit_commit_not_found(self,
                                         mock_gpid,
                                         mock_grc,
                                         mock_grcd):
        self.assertEquals([('FAIL', 'Commit not found: aaabbb', 1)],
                          self.flow.get_commit._fn(self.flow, 'aaabbb'))

    sample_commit_details = {
        'author_name': 'Jane Doe',
        'message': 'foo_message',
        'created_at': 'foo_date'
    }

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getrepositorycommit',
                return_value=sample_commit_details)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getrepositorycommitdiff',
                return_value=False)
    def test_get_commit_sample_commit_details(self,
                                              mock_gpid,
                                              mock_grc,
                                              mock_grcd):
        self.assertEquals([('BOLD', 'COMMIT: aaabbb'),
                           ('GREEN', 'AUTHOR: Jane Doe'),
                           ('GREEN', 'MESSAGE:\nfoo_message'),
                           ('GREEN', 'DATE: foo_date')],
                          self.flow.get_commit._fn(self.flow, 'aaabbb'))

    # With diff
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getrepositorycommit',
                return_value=sample_commit_details)
    @mock.patch('nacl.gitlabapi.GitLapApiCall.getrepositorycommitdiff',
                return_value=[{'diff': 'foo_diff'}])
    def test_get_commit_sample_commit_details_with_diff(self,
                                                        mock_gpid,
                                                        mock_grc,
                                                        mock_grcd):
        self.assertEquals([('BOLD', 'COMMIT: aaabbb'),
                           ('GREEN', 'AUTHOR: Jane Doe'),
                           ('GREEN', 'MESSAGE:\nfoo_message'),
                           ('GREEN', 'DATE: foo_date'),
                           ('GREEN', 'DIFF:\n'),
                           ('BOLD', '\nfoo_diff')],
                          self.flow.get_commit._fn(self.flow, 'aaabbb'))

if __name__ == '__main__':
    unittest.main()
