#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock

# from nacl.gitapi import get_remote_url_dict
from nacl.gitapi import clean_up_repositorie

class TestNaclGitApi(unittest.TestCase):

    # get_remote_url_dict
    @mock.patch("nacl.fileutils.get_users_nacl_conf", side_effect={'ignore_repositories': ['foo', 'bar'], 'gitapiserver': 'server', 'gitapitoken': 'AAbbCC'})
    def test_get_remote_url_dict(self, mock):
        pass

    # clean_up_repositorie
    def test_clean_up_repositorie(self):
        test_dict = {'foo': 1, 'bar': 2, 'baz': 3}
        test_ignore_list = ['bar']
        result_dict = {'foo': 1, 'baz': 3}
        self.assertEqual(clean_up_repositorie(test_dict, test_ignore_list), result_dict)
