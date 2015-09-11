#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from nacl.gitapi import get_gitgitlab_handle
from nacl.gitapi import get_remote_url_dict


class TestNaclGitApi(unittest.TestCase):

    # get_gitgitlab_handle()

    @mock.patch('vendor.gitlab.Gitlab', return_value='foo')
    def test_get_gitlab_handle(self, mock):
        self.assertEquals('foo', get_gitgitlab_handle('bar', 'baz'))

    # get_remote_url_dict()

    sample_user_config_1 = {
        'ignore_repositories': ['foo', 'bar'],
        'gitapiserver': 'server',
        'gitapitoken': 'AAbbCC',
        'gitgroup': 'saltstack'
    }

    sample_user_config_2 = {
        'gitapiserver': 'server',
        'gitapitoken': 'AAbbCC',
        'gitgroup': 'u_saltstack'
    }

    # Mocking git.getgroups() the hard way
    def return_handle(host, token):
        class Foo:
            def getgroups(self, group_id=None):
                sample_group = [{
                    'name': 'saltstack',
                    'id': 123,
                    'projects': [{
                        'ssh_url_to_repo': 'ssh_url',
                        'description': 'foo'
                    }]
                }]

                sample_projects = {
                    'name': 'saltstack',
                    'id': 123,
                    'projects': [{
                        'ssh_url_to_repo': 'ssh_url',
                        'description': 'foo'
                    }]
                }
                if group_id:
                    return sample_projects
                else:
                    return sample_group
        return Foo()

    @mock.patch("nacl.gitapi.get_users_nacl_conf",
                return_value=sample_user_config_1)
    @mock.patch('nacl.gitapi.get_gitgitlab_handle', return_value=None)
    def test_get_remote_url_dict_fail1(self,
                                       mock_config,
                                       mock_handle):
        self.assertEqual([('FAIL', 'API call failed! Credentials?', 1)],
                         get_remote_url_dict._fn())

    @mock.patch("nacl.gitapi.get_users_nacl_conf",
                return_value=sample_user_config_2)
    @mock.patch('nacl.gitapi.get_gitgitlab_handle', return_value=None)
    def test_get_remote_url_dict_fail2(self,
                                       mock_config,
                                       mock_handle):
        self.assertEqual([('FAIL', 'API call failed! Credentials?', 1)],
                         get_remote_url_dict._fn())

    # test with gitgroup providing a group
    @mock.patch("nacl.gitapi.get_users_nacl_conf",
                return_value=sample_user_config_1)
    @mock.patch('nacl.gitapi.get_gitgitlab_handle', side_effect=return_handle)
    def test_get_remote_url_dict_group(self,
                                       mock_config,
                                       mock_handle):
        self.assertEqual({'payload': {'ssh_url': 'foo'}},
                         get_remote_url_dict._fn())

    # test with gitgroup providing groups but the user has
    # named a unknown group as well
    @mock.patch("nacl.gitapi.get_users_nacl_conf",
                return_value=sample_user_config_2)
    @mock.patch('nacl.gitapi.get_gitgitlab_handle', side_effect=return_handle)
    def test_get_remote_url_dict_unknown_group(self,
                                               mock_config,
                                               mock_handle):
        self.assertEqual([('FAIL', 'Git group not found: u_saltstack', 1)],
                         get_remote_url_dict._fn())

if __name__ == '__main__':
    unittest.main()
