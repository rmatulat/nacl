#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
import pprint
from nacl.git import branch_is_clean
from nacl.git import need_pull_push
from nacl.git import is_merged
from nacl.git import is_git_repo
from nacl.git import get_all_branches
from nacl.git import branch_exist
from nacl.git import get_last_commit_sha
from nacl.git import is_commit_on_remote
from nacl.git import get_current_branch
from nacl.git import git
from nacl.exceptions import GitCallError
from nacl.git import list_git_repositories
from nacl.git import remote_diff
from nacl.git import checkout_branch


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
    def test_is_merged_false(self, nacl_git_mock):
        self.assertFalse(is_merged("foo_branch"))

    # is_git_repo()
    # this is weird because I can switch the mocked module to
    # whatever I like as long as it is a valid module?!
    @mock.patch('os.path.exists', side_effect=[True])
    def test_is_git_repo(self, os_mock):
        self.assertTrue(is_git_repo())

    # get_all_branches()
    @mock.patch('nacl.git.git', side_effect=["foo_branch"])
    def test_get_all_branches(self, git_mock):
        self.assertEqual(get_all_branches(), ["foo_branch"])

    # branch_exists()
    @mock.patch('nacl.git.get_all_branches', side_effect=[["b1", "b2", "b3"]])
    def test_branch_exists_1(self, mock):
        self.assertTrue(branch_exist("b2"))

    @mock.patch('nacl.git.get_all_branches', side_effect=[["b1", "b2", "b3"]])
    def test_branch_exists_2(self, mock):
        self.assertFalse(branch_exist("b4"))

    # get_last_commit_sha()
    @mock.patch('nacl.git.git', side_effect=["aaaabbbbcccc"])
    def test_get_last_commit_sha(self, mock):
        self.assertEqual(get_last_commit_sha(), "aaaabbbbcccc")

    # is_commit_on_remote()
    @mock.patch('nacl.git.git', side_effect=["aaaabbbbcccc"])
    def test_is_commit_on_remote_1(self, mock):
        self.assertTrue(is_commit_on_remote("aaaabbbbcccc"))

    @mock.patch('nacl.git.git', side_effect=["aaaabbbbcccc"])
    def test_is_commit_on_remote_2(self, mock):
        self.assertFalse(is_commit_on_remote("ddddeeeefff"))

    # is_commit_on_remote is called without () to get assertRaises working...
    @mock.patch('nacl.git.git', side_effect=["aaaabbbbcccc"])
    def test_is_commit_on_remote_3(self, mock):
        self.assertRaises(ValueError, is_commit_on_remote)

    # get_current_branch()
    @mock.patch('nacl.git.git', side_effect=["master"])
    def test_get_current_branch(self, mock):
        self.assertEqual(get_current_branch(), "master")

    # git()

    # normal git call
    @mock.patch('subprocess.Popen.communicate', return_value=('foo', None))
    @mock.patch('subprocess.Popen.wait', return_value=0)
    def test_git(self, mock_wait, mock_communicate):
        self.assertEquals('foo', git(['foo']))

    # raises GitCallError
    @mock.patch('subprocess.Popen.communicate', return_value=('foo', 'bar'))
    @mock.patch('subprocess.Popen.wait', return_value=1)
    def test_raise_git_call_error(self, mock_wait, mock_communicate):
        self.assertRaises(GitCallError, lambda: git(['foo']))

    # providing an env
    @mock.patch('subprocess.Popen.communicate', return_value=('foo', None))
    @mock.patch('subprocess.Popen.wait', return_value=0)
    def test_git_providing_env(self, mock_wait, mock_communicate):
        self.assertEquals('foo', git(['foo'], env={'foo': 'bar'}))

    # list_git_repositories (partly)
    #
    # THIS IS SPECIAL, AND I HAVE TO NOTE IT TO MYSELF:
    # It's about testing a decorated function.
    #
    # First: Note list_git_repositories._fn()
    # We are calling the origin func() that is stored in the decorators object
    # variable _fn. We are NOT calling list_git_repositories() as it
    # will be decorated at execution with all the decoration actually done.
    #
    # NEXT GOTCHA, THAT COSTS ME HOURS TO FIGURE OUT:
    # Where to patch:
    # http://www.voidspace.org.uk/python/mock/patch.html#where-to-patch
    #
    # get_dir_list_from_filesystem is located in nacl.fileutils.
    # BUT:
    # It is imported in nacl.git like so:
    # from nacl.fileutils import get_dir_list_from_filesystem
    #
    # So now get_dir_list_from_filesystem has to be mocked in nacl.git, because
    # it is imported into it!
    @mock.patch('nacl.git.get_dir_list_from_filesystem', return_value=[])
    def test_list_git_repositories(self, mock_fu):
        self.assertEqual([('WARNING', 'No git repository provided!', 3)], list_git_repositories._fn())

    # remote_diff()

    # branch is not clean and no diffs found
    @mock.patch('nacl.git.branch_is_clean', return_value=False)
    @mock.patch('nacl.git.git', return_value=None)
    def test_remote_diff_branch_not_clean(self, mock_branch, mock_git):
        self.assertEquals([('INFO', 'Uncommitted changes.'), ('INFO', 'No diffs found')], remote_diff._fn())

    # branch is clean and pseudo diffs found
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.git', return_value='foo')
    def test_remote_diff_branch_clean(self, mock_branch, mock_git):
        self.assertEquals([('INFO', 'foo')], remote_diff._fn())

    # checkout_branch()
    # First Check: branch is not provided
    @mock.patch('nacl.git.git', return_value='bar')
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.print_is_git_repo', return_value=None)
    def test_checkout_branch_branch_is_none(self,
                                            mock_git,
                                            mock_gcb,
                                            mock_pigr):
        self.assertEqual([('INFO', 'Branch: foo')], checkout_branch._fn(None))

    # 2nd Check: branch is provided and already active
    @mock.patch('nacl.git.git', return_value='bar')
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.print_is_git_repo', return_value=None)
    def test_checkout_branch_branch_is_active(self,
                                              mock_git,
                                              mock_gcb,
                                              mock_pigr):
        self.assertEqual([('INFO', 'Already in foo')], checkout_branch._fn('foo'))

    # 3rd Check: branch is provided and NOT active
    @mock.patch('nacl.git.git', return_value='bar')
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.print_is_git_repo', return_value=None)
    def test_checkout_branch_branch_is_not_active(self,
                                                  mock_git,
                                                  mock_gcb,
                                                  mock_pigr):
        self.assertEqual([('INFO', 'Switch to branch: foo')], checkout_branch._fn('bar'))

    def git_side_effect(args):
        raise ValueError

    # 4th Check: raise Exception
    @mock.patch('nacl.git.git', side_effect=git_side_effect)
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.print_is_git_repo', return_value=None)
    def test_checkout_branch_raises(self,
                                    mock_git,
                                    mock_gcb,
                                    mock_pigr):
        self.assertRaises(ValueError, lambda: checkout_branch._fn('bar'))

if __name__ == '__main__':
    unittest.main()
