#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from nacl.fileutils import binary_exists
from nacl.fileutils import get_dir_list_from_filesystem


class TestNaclFileUtils(unittest.TestCase):

    # binary_exists()

    def test_binary_exists(self):
        self.assertTrue(binary_exists('ls'))
        self.assertFalse(binary_exists('not_existing'))

    # get_dir_list_from_filesystem()

    @mock.patch('nacl.fileutils.get_salt_root_dirs', return_value=['/bar'])
    @mock.patch('os.walk',
                return_value=[('/fooo/.git', 'dirname', 'filename')])
    def test_get_dir_list_from_filesystem_filter_set(self,
                                                     mock_gsrd,
                                                     mock_oswalk):
        self.assertEqual(['/fooo/.git'], get_dir_list_from_filesystem('*.git'))

    @mock.patch('nacl.fileutils.get_salt_root_dirs', return_value=['/bar'])
    @mock.patch('os.walk',
                return_value=[('/fooo/.git', 'dirname', 'filename')])
    def test_get_dir_list_from_filesystem_no_filter(self,
                                                    mock_gsrd,
                                                    mock_oswalk):
        self.assertEqual(['/fooo/.git'], get_dir_list_from_filesystem())


if __name__ == '__main__':
    unittest.main()
