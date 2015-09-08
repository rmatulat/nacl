#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
import nacl.helper


class TestNaclHelper(unittest.TestCase):

    # color()

    def test_color(self):
        self.assertEqual('\x1b[94mtext\x1b[0m', nacl.helper.color('INFO', 'text'))

    # query_yes_no()

    @mock.patch('__builtin__.raw_input', return_value='Y')
    def test_yes_no_Yes(self, mock):
        self.assertTrue(nacl.helper.query_yes_no('question'))

    @mock.patch('__builtin__.raw_input', return_value='N')
    def test_yes_no_No(self, mock):
        self.assertFalse(nacl.helper.query_yes_no('question'))

    @mock.patch('__builtin__.raw_input', return_value='N')
    def test_yes_no_default_None(self, mock):
        self.assertFalse(nacl.helper.query_yes_no('question', default=None))

    @mock.patch('__builtin__.raw_input', return_value='N')
    def test_yes_no_default_no(self, mock):
        self.assertFalse(nacl.helper.query_yes_no('question', default='no'))

    @mock.patch('__builtin__.raw_input', return_value='')
    def test_yes_no_empty_choice(self, mock):
        self.assertTrue(nacl.helper.query_yes_no('question'))

    @mock.patch('__builtin__.raw_input', return_value='Y')
    def test_yes_no_raises(self, mock):
        self.assertRaises(ValueError,
                          lambda: nacl.helper.query_yes_no(
                              'question',
                              default="foo"))

    # merge_two_dicts

    def test_merge_two_dicts(self):
        a = {'foo': 1}
        b = {'bar': 2}
        self.assertEqual({'bar': 2, 'foo': 1}, nacl.helper.merge_two_dicts(a, b))

    # clean_up_repositories()
    def test_clean_up_repositorie(self):
        test_dict = {'foo': 1, 'bar': 2, 'baz': 3}
        test_ignore_list = ['bar']
        result_dict = {'foo': 1, 'baz': 3}
        self.assertEqual(result_dict, nacl.helper.clean_up_dict(test_dict, test_ignore_list))

if __name__ == '__main__':
    unittest.main()
