#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from nacl.fileutils import binary_exists
from nacl.fileutils import get_dir_list_from_filesystem
from nacl.fileutils import get_users_nacl_conf


class TestNaclFileUtils(unittest.TestCase):

    # binary_exists()

    def test_binary_exists(self):
        self.assertTrue(binary_exists('ls'))
        self.assertFalse(binary_exists('not_existing'))

    # get_dir_list_from_filesystem()

    @mock.patch('nacl.fileutils.get_salt_root_dirs', return_value=['/bar'])
    @mock.patch('os.walk',
                return_value=[('/fooo/.git', 'dirname', 'filename')])
    def test_get_dir_list_from_filesystem_foo_git(self,
                                                  mock_gsrd,
                                                  mock_oswalk):
        self.assertEqual(['/fooo/.git'], get_dir_list_from_filesystem('*.git'))

    def test_get_dir_list_from_filesystem(self):
        """ Only checks whether a list is returned """
        self.assertEqual([], get_dir_list_from_filesystem())

    # get_users_nacl_conf()

    @mock.patch('os.path.expanduser', return_value="/tmp/")
    @mock.patch('__builtin__.open')
    @mock.patch('json.load', return_value="{'foo': 'bar'}")
    def test_get_users_nacl_conf(self, os_mock, open_mock, json_mock):
        self.assertEqual("{'foo': 'bar'}", get_users_nacl_conf())

    # test the except block
    @mock.patch('os.path.expanduser', return_value="/tmp/")
    @mock.patch('__builtin__.open')
    @mock.patch('json.load', side_effect=TypeError())
    def test_get_users_nacl_conf_raises(self, os_mock, open_mock, json_mock):
        self.assertEqual([('FAIL', ' ~/.nacl not found or invalid JSON', 3)],
                         get_users_nacl_conf._fn())

if __name__ == '__main__':
    unittest.main()
