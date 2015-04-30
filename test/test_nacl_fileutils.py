#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest


class TestNaclFileUtils(unittest.TestCase):

    def test_binary_exists(self):
        from nacl.fileutils import binary_exists
        self.assertTrue(binary_exists('ls'))
        self.assertFalse(binary_exists('not_existing'))

    def test_get_salt_start_dir(self):
        from nacl.fileutils import get_salt_start_dir
        self.assertEqual(get_salt_start_dir(), ['/srv/pillar', '/srv/salt'])

    def test_get_dir_list_from_filesystem(self):
        """ Only checks whether a list is returned """
        from nacl.fileutils import get_dir_list_from_filesystem
        self.assertIsInstance(get_dir_list_from_filesystem(), list)

if __name__ == '__main__':
    unittest.main()
