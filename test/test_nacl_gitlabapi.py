#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
import pprint
from nacl.gitlabapi import GitLapApiCall


class TestNaclGitLapApiCall(unittest.TestCase):
    """ We are doing some extensive mocking over here. Maybe it is
        because I have wrote crappy code or maybe there is no other way."""
    fake_config = {
        u'gitapiserver': u'http://gitlab.example.com/',
        u'gitapitoken': u'AweSomeToken',
        u'gitgroup': u'saltstack',
        u'githostertype': u'gitlab',
        u'ignore_repositories': [
            u'git@gitlab.example.com:saltstack/foo.git',
            u'git@gitlab.example.com:saltstack/bar.git',
            u'git@gitlab.example.com:saltstack/baz.git',
            u'git@gitlab.example.com:saltstack/foz.git']}

    @mock.patch(
        "nacl.gitlabapi.get_users_nacl_conf",
        side_effect=[fake_config])
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_project_id',
                return_value=123)
    def setUp(self, config_mock, mock_pid):
        self.git = GitLapApiCall()

    # get_project_id
    @mock.patch("nacl.git.git",
                side_effect=["http://gitlab.example.com/foo.git"])
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getproject",
                return_value={'id': 22})
    @mock.patch("nacl.git.is_git_repo", return_value=True)
    def test_get_project_id_success(self,
                                    mock_git,
                                    mock_getproject,
                                    is_git_mock):
        self.assertEqual(self.git.get_project_id(), 22)

    @mock.patch("nacl.git.git",
                side_effect=["http://gitlab.example.com/foo.git"])
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getproject",
                return_value=False)
    @mock.patch("nacl.git.is_git_repo", return_value=True)
    def test_get_project_id_false(self,
                                  mock_git,
                                  mock_getproject,
                                  mock_is_git):
        self.assertFalse(self.git.get_project_id())

    @mock.patch("nacl.git.git",
                side_effect=["http://gitlab.example.com/foo.git"])
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getproject",
                return_value={'id': 22})
    @mock.patch("nacl.git.is_git_repo", return_value=False)
    def test_get_project_id_sys_exit(self,
                                     mock_git,
                                     mock_getproject,
                                     mock_is_git):
        self.assertRaises(SystemExit, self.git.get_project_id)

    # _get_seperator()
    def test_get_seperator(self):
        self.assertEqual(self.git._get_seperator(), 'gitlab.example.com')

    # get_group_id
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getgroups",
                return_value=[{'name': 'saltstack', 'id': 6}])
    def test_get_group_id_success(self, mock_getgroups):
        self.assertEqual(self.git.get_group_id(), 6)

    @mock.patch("nacl.gitlabapi.GitLapApiCall.getgroups",
                return_value=[{'name': 'saltstack'}])
    def test_get_group_id_false(self, mock_getgroups):
        self.assertFalse(self.git.get_group_id())

    # is_mergerequest_new
    def test_is_mergerequest_new_raises(self):
        self.assertRaises(ValueError, self.git.is_mergerequest_new)

    mergerequest_1 = [
        {'state': 'closed',
         'source_branch': 'foo',
         'target_branch': 'foo'}]

    # this is true because 'state' == 'closed'
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getproject",
                return_value={'id': 22})
    @mock.patch("nacl.git.git",
                side_effect=["http://gitlab.example.com/foo.git"])
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getmergerequests",
                return_value=mergerequest_1)
    @mock.patch("nacl.git.is_git_repo", return_value=True)
    def test_is_mergerequest_new_for_loop_true(self,
                                               mock_p_id,
                                               mock_git,
                                               mock_getmr,
                                               mock_is_git):
        self.assertTrue(self.git.is_mergerequest_new('foo', 'foo'))

    mergerequest_2 = [
        {'state': 'open',
         'source_branch': 'foo',
         'target_branch': 'foo'}]

    @mock.patch("nacl.gitlabapi.GitLapApiCall.getproject",
                return_value={'id': 22})
    @mock.patch("nacl.git.git",
                side_effect=["http://gitlab.example.com/foo.git"])
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getmergerequests",
                return_value=mergerequest_2)
    @mock.patch("nacl.git.is_git_repo", return_value=True)
    def test_is_mergerequest_new_for_loop_false(self,
                                                mock_p_id,
                                                mock_git,
                                                mock_getmr,
                                                mock_is_git):
        self.assertFalse(self.git.is_mergerequest_new('foo', 'foo'))

    # this is true due to different branches
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getproject",
                return_value={'id': 22})
    @mock.patch("nacl.git.git",
                side_effect=["http://gitlab.example.com/foo.git"])
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getmergerequests",
                return_value=mergerequest_2)
    @mock.patch("nacl.git.is_git_repo", return_value=True)
    def test_is_mergerequest_new_for_loop_true_2(self,
                                                 mock_p_id,
                                                 mock_git,
                                                 mock_getmr,
                                                 mock_is_git):
        self.assertTrue(self.git.is_mergerequest_new('foo', 'bar'))

    # is_mergerequest_open()
    def test_is_mergerequest_open(self):
        self.assertRaises(ValueError, self.git.is_mergerequest_open)

    mergerequest_details = {'changes': {'state': 'opened'}}

    @mock.patch("nacl.gitlabapi.GitLapApiCall.get_mergerequest_details",
                return_value=mergerequest_details)
    def test_is_mergerequest_open_true(self, mock):
        self.assertTrue(self.git.is_mergerequest_open(1))

    mergerequest_details_2 = {'changes': {'state': 'closed'}}

    @mock.patch("nacl.gitlabapi.GitLapApiCall.get_mergerequest_details",
                return_value=mergerequest_details_2)
    def test_is_mergerequest_open_false(self, mock):
        self.assertFalse(self.git.is_mergerequest_open(1))

    mergerequest_details_3 = {}

    @mock.patch("nacl.gitlabapi.GitLapApiCall.get_mergerequest_details",
                return_value=mergerequest_details_3)
    def test_is_mergerequest_open_false_2(self, mock):
        self.assertFalse(self.git.is_mergerequest_open(1))

    # get_all_issues()
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getprojectissues",
                return_value=False)
    def test_get_all_issues_raises(self, mock):
        self.assertRaises(TypeError, self.git.get_all_issues)

    @mock.patch("nacl.gitlabapi.GitLapApiCall.getprojectissues",
                return_value={'foo': 'bar'})
    def test_get_all_issues_returns_something(self,
                                              mock_get_p_issues):
        self.assertEqual(self.git.get_all_issues(), {'foo': 'bar'})

    # list_group_members()
    @mock.patch("nacl.gitlabapi.GitLapApiCall.get_group_id",
                return_value=22)
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getgroupmembers",
                return_value={'foo': 'bar'})
    def test_list_group_members(self,
                                mock_g_id,
                                mock_get_gm):
        self.assertEqual(self.git.list_group_members(), {'foo': 'bar'})

    # edit_issue()
    def test_edit_issue(self):
        self.assertRaises(ValueError, self.git.edit_issue)

    @mock.patch("nacl.gitlabapi.GitLapApiCall.editissue",
                return_value={'foo': 'bar'})
    def test_edit_issue_returns_something(self, mock_ei):
        self.assertEqual(self.git.edit_issue(11), {'foo': 'bar'})

    # issue_iid_to_uid()
    def test_issue_iid_to_uid_raises(self):
        self.assertRaises(ValueError, self.git.issue_iid_to_uid)

    all_project_issues = [{
        'iid': 11,
        'id': 1
    }]

    @mock.patch("nacl.gitlabapi.GitLapApiCall.get_all_issues",
                return_value=all_project_issues)
    def test_issue_iid_to_uid_id_returned(self, mock):
        self.assertEqual(self.git.issue_iid_to_uid(11), 1)

    @mock.patch("nacl.gitlabapi.GitLapApiCall.get_all_issues",
                return_value=all_project_issues)
    def test_issue_iid_to_uid_id_not_found(self, mock):
        self.assertFalse(self.git.issue_iid_to_uid(22))

    # get_mergerequest_details()
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getmergerequestchanges",
                return_value='foo')
    @mock.patch("nacl.gitlabapi.GitLapApiCall.getmergerequestcomments",
                return_value='bar')
    @mock.patch("nacl.git.git",
                side_effect=["http://gitlab.example.com/foo.git"])
    @mock.patch("nacl.git.is_git_repo", return_value=True)
    def test_get_mergerequest_details(self,
                                      mock_get_mr_c,
                                      mock_get_mr_d,
                                      mock_git,
                                      mock_is_git):
        self.assertEqual(self.git.get_mergerequest_details(1), {'changes': 'foo', 'comments': 'bar'})

    # mr_is_mergeable()
    def test_mr_is_mergeable_raises(self):
        self.assertRaises(ValueError, self.git.mr_is_mergeable)

    mergerequest_details_mergeable = {
        'changes': {
            'source_branch': 'issue_1',
            'target_branch': 'issue_1'}}

    @mock.patch("nacl.gitlabapi.GitLapApiCall.get_mergerequest_details",
                return_value=mergerequest_details_mergeable)
    @mock.patch("nacl.git.get_current_branch", return_value='master')
    @mock.patch("nacl.git.branch_is_clean", return_value=True)
    @mock.patch("nacl.git.git", return_value=True)
    def test_mr_is_mergeable_true(self,
                                  mock_mr_d,
                                  mock_current_b,
                                  mock_branch_ic,
                                  mock_git):
        self.assertTrue(self.git.mr_is_mergeable(666))

    @mock.patch("nacl.gitlabapi.GitLapApiCall.get_mergerequest_details",
                return_value=mergerequest_details_mergeable)
    @mock.patch("nacl.git.get_current_branch", return_value='master')
    @mock.patch("nacl.git.branch_is_clean", return_value=False)
    @mock.patch("nacl.git.git", return_value=True)
    def test_mr_is_mergeable_reverse_stash(self,
                                           mock_mr_d,
                                           mock_current_b,
                                           mock_branch_ic,
                                           mock_git):
        self.assertTrue(self.git.mr_is_mergeable(666))

    # We need this helper_func to fake a failed nacl.git.git() call
    def is_mr_sideeffect(args):
        if args != ['merge', 'tmp_issue_1', 'tmp_issue_1']:
            pass
        else:
            raise ValueError

    @mock.patch("nacl.gitlabapi.GitLapApiCall.get_mergerequest_details",
                return_value=mergerequest_details_mergeable)
    @mock.patch("nacl.git.get_current_branch", return_value='master')
    @mock.patch("nacl.git.branch_is_clean", return_value=False)
    @mock.patch("nacl.git.git", side_effect=is_mr_sideeffect)
    def test_mr_is_mergeable_branch_not_clean_and_false(self,
                                                        mock_mr_d,
                                                        mock_current_b,
                                                        mock_branch_ic,
                                                        mock_git):
        self.assertFalse(self.git.mr_is_mergeable(666))

    # We simulate a failed git merge
    @mock.patch("nacl.gitlabapi.GitLapApiCall.get_mergerequest_details",
                return_value=mergerequest_details_mergeable)
    @mock.patch("nacl.git.get_current_branch", return_value='master')
    @mock.patch("nacl.git.branch_is_clean", return_value=True)
    @mock.patch("nacl.git.git", side_effect=is_mr_sideeffect)
    def test_mr_is_mergeable_false(self,
                                   mock_mr_d,
                                   mock_current_b,
                                   mock_branch_ic,
                                   mock_git):
        self.assertFalse(self.git.mr_is_mergeable(666))

    # accept_mergerequest()
    def test_accept_mergerequest(self):
        self.assertRaises(ValueError, self.git.accept_mergerequest)

    @mock.patch("nacl.gitlabapi.GitLapApiCall.acceptmergerequest",
                return_value=True)
    def test_accept_mergerequest_true(self, mock_am):
        self.assertTrue(self.git.accept_mergerequest(666))

    # remote_branch_exists()
    def test_remote_branch_exists(self):
        self.assertRaises(ValueError, self.git.remote_branch_exists)

    @mock.patch("nacl.gitlabapi.GitLapApiCall.getbranch",
                return_value='foo')
    def test_remote_branch_remote_exists(self, mock):
        self.assertTrue(self.git.remote_branch_exists('foo'))

    @mock.patch("nacl.gitlabapi.GitLapApiCall.getbranch",
                side_effect=[Exception('boo')])
    def test_remote_branch_raises(self, mock):
        self.assertFalse(self.git.remote_branch_exists('foo'))
