#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Test the decorator.py """

import unittest
from io import StringIO
import sys
import mock
import pprint
from nacl.decorator import ListLine, log


class TestLog(unittest.TestCase):

    """
    First part: Testing log

    The first (and most used) decorator will be tested here.
    Therefore we define a sample function in each test, returning different
    lists with tuples.
    We mock sys.stdout and sys.stderr because Log will not return anything -
    it just prints stuff out. So we need to catch the output and assert.
    """

    # Test log()

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_log_a(self, mock):
        @log
        def dummy():
            return [('INFO', 'foo')]
        dummy()
        output = mock.getvalue()
        self.assertEqual(u'[ INFO ] \x1b[94mfoo\x1b[0m\n', output)

    @mock.patch('sys.exit', return_value=None)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_log_b(self, mock_stdout, mock):
        @log
        def dummy():
            return [('INFO', 'foo', 1)]

        dummy()
        output = mock_stdout.getvalue()
        self.assertEqual(u'[ WARN ] \x1b[94mfoo\x1b[0m\n', output)

    @mock.patch('sys.exit', return_value=None)
    def test_log_c(self, mock):
        @log
        def dummy():
            return [('INFO', 'foo', 'foo')]

        self.assertRaises(ValueError, dummy)

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_log_d(self, mock):
        @log
        def dummy():
            return [('FAIL', 'foo')]
        dummy()
        output = mock.getvalue()
        self.assertEqual(u'[ INFO ] \x1b[91mfoo\x1b[0m\n', output)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_log_e(self, mock):
        """ We will just return, if there are no messages passed """
        @log
        def dummy():
            return []
        dummy()
        output = mock.getvalue()
        self.assertEqual(u'', output)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_log_f(self, mock):
        """ tuble with an int has no attribute len(), so we
            fail here with an TypeError"""
        @log
        def dummy():
            return [(1)]
        self.assertRaises(TypeError, dummy)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_log_g(self, mock):
        """ We will just return, if there are no messages passed """
        @log
        def dummy():
            return [('a')]
        self.assertRaises(ValueError, dummy)

    # Test ListLine decorator
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_ListLine_a(self, mock):
        """ decorator returns nothing """
        @ListLine
        def dummy():
            return []
        dummy()
        output = mock.getvalue()
        self.assertEqual(u'', output)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_ListLine_b(self, mock):
        """ decorator returns trash """
        @ListLine
        def dummy():
            return ['foo']
        self.assertRaises(TypeError, dummy)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_ListLine_dicts(self, mock):
        test_list_dict = [
            {'status': 'foo'},
            {'status': 'foo', 'merge_status': 'bar'},
            {'status': 'foo', 'merge_status': '(merged)'},
            {'status': 'Clean', 'merge_status': '(merged)'},
            {'status': 'Clean',
             'merge_status': '(merged)',
             'pull_push': 'baz'},
            {'status': 'Clean',
             'merge_status': '(merged)',
             'pull_push': 'baz',
             'dir_name': '/foo/bar'}]
        for ret in test_list_dict:
            @ListLine
            def dummy():
                return ret

            self.assertRaises(KeyError, dummy)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_ListLine_c(self, mock):
        """ decorator returns nothing """
        @ListLine
        def dummy():
            return {
                'status': u'Clean',
                'merge_status': u'',
                'branch': u'master',
                'pull_push': u'Need to pull',
                'dir_name': u'/srv/salt/base/tools',
                'all_branches': u'issue_1, master, test1, test1_12345678'}
        dummy()
        output = mock.getvalue()
        self.assertEqual(u'\x1b[1G\x1b[93m/srv/salt/base/tools\x1b[0m\x1b[52G\x1b[92mmaster\x1b[0m\x1b[58G\x1b[91m\x1b[0m\x1b[68G\x1b[4mClean\x1b[0m\x1b[84G\x1b[91mNeed to pull\x1b[0m\x1b[100G\x1b[36missue_1, master, test1, test1_12345678\x1b[0m\n', output)

if __name__ == '__main__':
    unittest.main()
