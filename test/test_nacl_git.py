#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
# import pprint
from nacl.git import branch_is_clean
from nacl.git import need_pull_push
from nacl.git import is_merged
from nacl.git import is_git_repo
from nacl.git import print_is_git_repo
from nacl.git import get_all_branches
from nacl.git import branch_exist
from nacl.git import get_last_commit_sha
from nacl.git import is_commit_on_remote
from nacl.git import get_current_branch
from nacl.git import get_local_url_list
from nacl.git import git
from nacl.exceptions import GitCallError
from nacl.git import list_salt_git_repositories
from nacl.git import remote_diff
from nacl.git import checkout_branch
from nacl.git import change_or_create_branch
from nacl.git import merge_git_repo
from nacl.git import remote_prune
from nacl.git import pretty_status
from nacl.git import print_merge_status
from nacl.git import get_user_name
from nacl.git import get_user_email
from nacl.git import set_user_name
from nacl.git import set_user_email
from nacl.git import get_all_possible_git_dirs


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

    @mock.patch('nacl.git.git', side_effect=[None, "a", "a", "b"])
    def test_need_pull_push_0_answer(self, whatever):
        self.assertEqual(need_pull_push(False), 'Up-to-date')

    @mock.patch('nacl.git.git', side_effect=[None, "a", "b", "a"])
    def test_need_pull_push_1_answer(self, whatever):
        self.assertEqual(need_pull_push(False), 'Need to pull')

    @mock.patch('nacl.git.git', side_effect=[None, "a", "b", "b"])
    def test_need_pull_push_2_answer(self, whatever):
        self.assertEqual(need_pull_push(False), 'Need to push')

    @mock.patch('nacl.git.git', side_effect=[None, "a", "b", "c"])
    def test_need_pull_push_3_answer(self, whatever):
        self.assertEqual(need_pull_push(False), 'Diverged')

    # is_merged()
    @mock.patch('nacl.git.git', side_effect=[None, "a", "a"])
    def test_is_merged_true(self, whatever):
        self.assertTrue(is_merged("foo_branch"))

    @mock.patch('nacl.git.git', side_effect=[None, "a", "b"])
    def test_is_merged_false(self, nacl_git_mock):
        self.assertFalse(is_merged("foo_branch"))

    # is_git_repo()
    @mock.patch('os.chdir', return_value=True)
    @mock.patch('nacl.git.git', return_value=True)
    def test_is_git_repo(self, os_mock, mock_git):
        self.assertTrue(is_git_repo())

    @mock.patch('os.chdir', return_value=True)
    @mock.patch('nacl.git.git', return_value=True)
    def test_is_git_repo_with_dir_name(self, os_mock, mock_git):
        self.assertTrue(is_git_repo('foo'))

    @mock.patch('os.chdir', return_value=True)
    @mock.patch('nacl.git.git', side_effect=GitCallError())
    def test_is_git_repo_raises(self, os_mock, mock_git):
        self.assertFalse(is_git_repo())

    @mock.patch('os.chdir', return_value=True)
    @mock.patch('nacl.git.git', side_effect=GitCallError())
    def test_is_git_repo_with_dir_name_raises(self, os_mock, mock_git):
        self.assertFalse(is_git_repo('foo'))

    # print_is_git_repo()
    @mock.patch('nacl.git.is_git_repo', return_value=False)
    def test_print_is_git_repo(self, is_git_mock):
        self.assertEquals([('WARNING', 'No git repository found!', 1)],
                          print_is_git_repo._fn())

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

    @mock.patch('nacl.git.git', side_effect=TypeError())
    def test_is_commit_on_remote_4(self, mock):
        self.assertFalse(is_commit_on_remote('aaa'))

    # get_current_branch()
    @mock.patch('nacl.git.git', side_effect=["master"])
    def test_get_current_branch(self, mock):
        self.assertEqual(get_current_branch(), "master")

    # get_user_name()

    @mock.patch('nacl.git.git', return_value='John Doe\n')
    def test_get_user_name_1(self, mock_git):
        self.assertEqual('John Doe', get_user_name())

    # get_user_email()

    @mock.patch('nacl.git.git', return_value='jane@doe.com\n')
    def test_get_user_email_1(self, mock_git):
        self.assertEqual('jane@doe.com', get_user_email())

    # set_user_name()
    @mock.patch('nacl.git.git', return_value=None)
    def test_set_user_name_1(self, mock_git):
        self.assertRaises(ValueError, lambda: set_user_name())

    @mock.patch('nacl.git.git', return_value=None)
    def test_set_user_name_2(self, mock_git):
        self.assertEqual(None, set_user_name('John Doe'))

    # set_user_email()
    @mock.patch('nacl.git.git', return_value=None)
    def test_set_user_email_1(self, mock_git):
        self.assertRaises(ValueError, lambda: set_user_email())

    @mock.patch('nacl.git.git', return_value=None)
    def test_set_user_email_2(self, mock_git):
        self.assertEqual(None, set_user_email('e@mail.com'))

    # git()

    # normal git call
    @mock.patch('subprocess.Popen.communicate', return_value=('foo', None))
    @mock.patch('subprocess.Popen.wait', return_value=0)
    @mock.patch('nacl.git.get_users_nacl_conf', return_value={})
    def test_git(self, mock_wait, mock_communicate, mock_conf):
        self.assertEquals('foo', git(['foo']))

    # raises GitCallError
    @mock.patch('subprocess.Popen.communicate', return_value=('foo', 'bar'))
    @mock.patch('subprocess.Popen.wait', return_value=1)
    @mock.patch('nacl.git.get_users_nacl_conf', return_value={})
    def test_raise_git_call_error(self,
                                  mock_wait,
                                  mock_communicate,
                                  mock_conf):
        self.assertRaises(GitCallError, lambda: git(['foo']))

    # providing an env
    @mock.patch('subprocess.Popen.communicate', return_value=('foo', None))
    @mock.patch('subprocess.Popen.wait', return_value=0)
    @mock.patch('nacl.git.get_users_nacl_conf',
                return_value={
                    'gitapiserver': 'foo',
                    'gitapitoken': 'bar'
                })
    def test_git_providing_env(self, mock_wait, mock_communicate, mock_guc):
        self.assertEquals('foo', git(['foo'], env={'foo': 'bar'}))

    # list_salt_git_repositories (partly)
    #
    # THIS IS SPECIAL, AND I HAVE TO NOTE IT TO MYSELF:
    # It's about testing a decorated function.
    #
    # First: Note list_salt_git_repositories._fn()
    # We are calling the origin func() that is stored in the decorators object
    # variable _fn. We are NOT calling list_salt_git_repositories() as it
    # will be decorated at execution with all the decoration actually done.
    #
    # NEXT GOTCHA, THAT TOOK ME HOURS TO FIGURE OUT:
    # Where to patch:
    # http://www.voidspace.org.uk/python/mock/patch.html#where-to-patch
    #
    # get_salt_root_dirs is located in nacl.fileutils.
    # BUT:
    # It is imported in nacl.git like this:
    # from nacl.fileutils import get_salt_root_dirs
    #
    # So now get_salt_root_dirs has to be mocked in nacl.git, because
    # it is imported into it!
    #
    # Note:
    # Upcoming tests mainly test strings (say: messages) that are returned by
    # the functions under tests.
    # When changing the messages one has to change the tests as well!

    @mock.patch('nacl.git.get_all_possible_git_dirs', return_value=[])
    def test_list_salt_git_repositories(self, mock_gapgd):
        self.assertEqual([('WARNING', 'No git repository provided!', 3)], list_salt_git_repositories._fn())

    # get_all_possible_git_dirs()
    @mock.patch('nacl.git.get_salt_root_dirs', return_value=['/foo'])
    @mock.patch('nacl.git.get_dir_list_from_filesystem',
                return_value=['/foo/.git', '/bar/.git'])
    @mock.patch('nacl.git.is_git_repo', return_value=True)
    def test_get_all_possible_git_dirs(self, mock_isgr, mock_gdlff, mock_gsrd):
        self.assertEqual(['/bar', '/foo'], get_all_possible_git_dirs())

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
        self.assertEquals([('BOLD', 'foo')], remote_diff._fn())

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

    # git raises an exception
    @mock.patch('nacl.git.git', side_effect=GitCallError())
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.print_is_git_repo', return_value=None)
    def test_checkout_branch_git_raises(self,
                                        mock_git,
                                        mock_gcb,
                                        mock_pigr):
        self.assertEqual([('FAIL', 'Unable to checkout bar : ')], checkout_branch._fn('bar'))

    def git_side_effect(args):
        raise GitCallError

    # change_or_create_branch()

    # No branch provided
    @mock.patch('nacl.git.git', return_value='foo')
    @mock.patch('nacl.git.print_is_git_repo', return_value=None)
    def test_change_or_create_branch(self, mock_git, mock_pigr):
        self.assertEquals([('INFO', 'foo')], change_or_create_branch._fn(None))

    # branch is provided but doesn't exists
    @mock.patch('nacl.git.git', return_value='bar')
    @mock.patch('nacl.git.print_is_git_repo', return_value=None)
    @mock.patch('nacl.git.branch_exist', return_value=False)
    def test_change_or_create_branch_branch_not_exists(self,
                                                       mock_git,
                                                       mock_pigr,
                                                       mock_be):
        self.assertEquals([('INFO', 'Creating branch: bar'), ('INFO', 'Switch into: bar')],
                          change_or_create_branch._fn('bar'))

    # branch is provided but doesn't exists
    @mock.patch('nacl.git.git', return_value='bar')
    @mock.patch('nacl.git.print_is_git_repo', return_value=None)
    @mock.patch('nacl.git.branch_exist', return_value=True)
    def test_change_or_create_branch_branch_exists(self,
                                                   mock_git,
                                                   mock_pigr,
                                                   mock_be):
        self.assertEquals([('INFO', 'Branch exists. Change into bar')],
                          change_or_create_branch._fn('bar'))

    # merge_git_repo()

    # Test git_repo_name is provided and branch is dirty
    @mock.patch('os.chdir', return_value=True)
    @mock.patch('os.getcwd', return_value='/foo/bar')
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=False)
    def test_merge_git_repo_branch_is_dirty(self,
                                            mock_bic,
                                            mock_gcb,
                                            mock_getcwd,
                                            mock_chdir):
        self.assertEquals([('INFO', 'Checking: /foo/bar'), ('INFO', 'Uncommitted changes, skipping...')],
                          merge_git_repo._fn('bar'))

    # Branch is clean and needs pull, master is active
    @mock.patch('os.chdir', return_value=True)
    @mock.patch('os.getcwd', return_value='/foo/bar')
    @mock.patch('nacl.git.get_current_branch', return_value='master')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.git', return_value='baz')
    @mock.patch('nacl.git.need_pull_push', return_value=1)
    def test_merge_git_repo_branch_is_clean(self,
                                            mock_npp,
                                            mock_git,
                                            mock_bic,
                                            mock_gcb,
                                            mock_getcwd,
                                            mock_chdir):
        self.assertEquals([('INFO', 'Checking: /foo/bar'),
                           ('INFO', 'Need merge! '),
                           ('INFO', 'Try to merge Branch: master in /foo/bar'),
                           ('INFO', 'Start merge...'),
                           ('INFO', 'Merge complete!')],
                          merge_git_repo._fn('bar'))

    # Branch is clean and needs pull, master is NOT active
    @mock.patch('os.chdir', return_value=True)
    @mock.patch('os.getcwd', return_value='/foo/bar')
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.git', return_value='baz')
    @mock.patch('nacl.git.need_pull_push', return_value=1)
    @mock.patch('nacl.git.checkout_branch', return_value=None)
    def test_merge_git_repo_branch_is_clean_not_master(self,
                                                       mock_cb,
                                                       mock_npp,
                                                       mock_git,
                                                       mock_bic,
                                                       mock_gcb,
                                                       mock_getcwd,
                                                       mock_chdir):
        self.assertEquals([('INFO', 'Checking: /foo/bar'),
                           ('INFO', 'Checkout master'),
                           ('INFO', 'Need merge! '),
                           ('INFO', 'Try to merge Branch: master in /foo/bar'),
                           ('INFO', 'Start merge...'),
                           ('INFO', 'Merge complete!'),
                           ('INFO', 'Switch back')],
                          merge_git_repo._fn('bar'))

    # Branch is clean but DON'T needs pull, master is NOT active
    @mock.patch('os.chdir', return_value=True)
    @mock.patch('os.getcwd', return_value='/foo/bar')
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.git', return_value='baz')
    @mock.patch('nacl.git.need_pull_push', return_value=0)
    @mock.patch('nacl.git.checkout_branch', return_value=None)
    def test_merge_git_repo_branch_no_pull_not_master(self,
                                                      mock_cb,
                                                      mock_npp,
                                                      mock_git,
                                                      mock_bic,
                                                      mock_gcb,
                                                      mock_getcwd,
                                                      mock_chdir):
        self.assertEquals([('INFO', 'Checking: /foo/bar'),
                           ('INFO', 'Checkout master'),
                           ('INFO', 'Nothing to do in master... Switch back')],
                          merge_git_repo._fn('bar'))

    # Raise Exception output test
    @mock.patch('os.chdir', return_value=True)
    @mock.patch('os.getcwd', return_value='/foo/bar')
    @mock.patch('nacl.git.get_current_branch', return_value='master')
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.git', side_effect=git_side_effect)
    @mock.patch('nacl.git.need_pull_push', return_value=1)
    @mock.patch('nacl.git.checkout_branch', return_value=None)
    def test_merge_git_repo_branch_raise_output(self,
                                                mock_cb,
                                                mock_npp,
                                                mock_git,
                                                mock_bic,
                                                mock_gcb,
                                                mock_getcwd,
                                                mock_chdir):
        self.assertEquals([('INFO', 'Checking: /foo/bar'),
                           ('INFO', 'Need merge! '),
                           ('INFO', 'Try to merge Branch: master in /foo/bar'),
                           ('INFO', 'Merge failed: ')], merge_git_repo._fn('bar'))

    # remote_prune()
    @mock.patch('nacl.git.git', return_value='')
    def test_remote_prune_output_none(self, mock):
        self.assertEquals([('INFO', 'Nothing to prune')], remote_prune._fn())

    @mock.patch('nacl.git.git', side_effect=GitCallError())
    def test_remote_prune_raises(self, mock):
        self.assertEquals([('FAIL', 'Prune failed: ')], remote_prune._fn())

    # get_local_url_list()
    @mock.patch('nacl.git.get_dir_list_from_filesystem', return_value=['foo'])
    @mock.patch('os.chdir', return_value=None)
    @mock.patch('nacl.git.git', return_value='git@foo.git')
    def test_get_local_url_list(self, mock_gdlff, mock_os, mock_git):
        self.assertEquals(['git@foo.git'], get_local_url_list())

    # pretty_status()
    # Branch is clean
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.git', return_value='M status')
    @mock.patch('nacl.git.need_pull_push', return_value='Yes')
    @mock.patch('nacl.git.get_all_branches', return_value=['a', 'b'])
    @mock.patch('nacl.git.branch_is_clean', return_value=True)
    @mock.patch('nacl.git.print_merge_status', return_value='baz')
    @mock.patch('os.getcwd', return_value='/foo/bar')
    def test_pretty_status(self,
                           mock_getcwd,
                           mock_ms,
                           mock_bic,
                           mock_gab,
                           mock_npp,
                           mock_git,
                           mock_gcb):
        self.assertEquals({'status': 'Clean', 'dir_name': '/foo/bar', 'pull_push': 'Yes', 'all_branches': 'a, b', 'branch': 'foo', 'merge_status': 'baz'}, pretty_status._fn())

    # Branch is not clean!
    @mock.patch('nacl.git.get_current_branch', return_value='foo')
    @mock.patch('nacl.git.git', return_value='M status')
    @mock.patch('nacl.git.need_pull_push', return_value='Yes')
    @mock.patch('nacl.git.get_all_branches', return_value=['a', 'b'])
    @mock.patch('nacl.git.branch_is_clean', return_value=False)
    @mock.patch('nacl.git.print_merge_status', return_value='baz')
    @mock.patch('os.getcwd', return_value='/foo/bar')
    def test_pretty_status_2(self,
                             mock_getcwd,
                             mock_ms,
                             mock_bic,
                             mock_gab,
                             mock_npp,
                             mock_git,
                             mock_gcb):
        self.assertEquals({'status': 'M status', 'dir_name': '/foo/bar', 'pull_push': 'Yes', 'all_branches': 'a, b', 'branch': 'foo', 'merge_status': 'baz'}, pretty_status._fn())

    # print_merge_status()
    @mock.patch('nacl.git.is_merged', return_value=True)
    def test_print_merge_status_1(self, mock):
        self.assertEquals('(merged)', print_merge_status('foo'))

    @mock.patch('nacl.git.is_merged', return_value=False)
    def test_print_merge_status_2(self, mock):
        self.assertEquals('(unmerged)', print_merge_status('foo'))

if __name__ == '__main__':
    unittest.main()
