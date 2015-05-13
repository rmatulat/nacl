#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from nacl.git import branch_is_clean
from nacl.git import need_pull_push
from nacl.git import is_merged
from nacl.git import is_git_repo


class TestNaclGit(unittest.TestCase):

    # branch_is_clean()
    @mock.patch('nacl.git.git', return_value=None)
    def test_branch_is_clean(self, whatever):
        self.assertTrue(branch_is_clean())

    @mock.patch('nacl.git.git', return_value="Some String")
    def test_branch_is_not_clean(self, whatever):
        self.assertFalse(branch_is_clean())

    # need_pull_push()
    @mock.patch('nacl.git.git', side_effect=[None, "a", "a", "b"])
    def test_need_pull_push_0(self, whatever):
        self.assertEqual(need_pull_push(True), 0)

    @mock.patch('nacl.git.git', side_effect=[None, "a", "b", "a"])
    def test_need_pull_push_1(self, whatever):
        self.assertEqual(need_pull_push(True), 1)

    @mock.patch('nacl.git.git', side_effect=[None, "a", "b", "b"])
    def test_need_pull_push_2(self, whatever):
        self.assertEqual(need_pull_push(True), 2)

    @mock.patch('nacl.git.git', side_effect=[None, "a", "b", "c"])
    def test_need_pull_push_3(self, whatever):
        self.assertEqual(need_pull_push(True), 3)

    # is_merged()
    @mock.patch('nacl.git.git', side_effect=[None, "a", "a"])
    def test_is_merged_true(self, whatever):
        self.assertTrue(is_merged("foo_branch"))

    @mock.patch('nacl.git.git', side_effect=[None, "a", "b"])
    def test_is_merged_false(self, whatever):
        self.assertFalse(is_merged("foo_branch"))

    # is_git_repo()
    # this is weird because I can switch the mocked module to
    # whatever I like as long as it is a valid module?!
    @mock.patch('os.path.exists', side_effect=[True])
    def test_is_git_repo(self, whatever):
        self.assertTrue(is_git_repo())

if __name__ == '__main__':
    unittest.main()
