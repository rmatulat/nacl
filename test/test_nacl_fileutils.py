#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from nacl.fileutils import binary_exists
from nacl.fileutils import get_salt_root_dirs
from nacl.fileutils import get_dir_list_from_filesystem
from nacl.fileutils import get_users_nacl_conf


class TestNaclFileUtils(unittest.TestCase):

    def test_binary_exists(self):
        self.assertTrue(binary_exists('ls'))
        self.assertFalse(binary_exists('not_existing'))

    def test_get_salt_root_dirs(self):
        self.assertIsInstance(get_salt_root_dirs(), list)

    def test_get_dir_list_from_filesystem(self):
        """ Only checks whether a list is returned """
        self.assertIsInstance(get_dir_list_from_filesystem(), list)

    # Mocking stuff away
    @mock.patch('os.path.expanduser', return_value="/tmp/")
    @mock.patch('__builtin__.open')
    @mock.patch('json.load', return_value="{ 'foo': 'bar' }")
    def test_get_users_nacl_conf(self, os_mock, open_mock, json_mock):
        self.assertTrue(get_users_nacl_conf())

if __name__ == '__main__':
    unittest.main()
