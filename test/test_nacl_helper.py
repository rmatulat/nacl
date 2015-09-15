#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
import nacl.helper
from io import StringIO


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

    # input_wrapper()

    def test_input_wrapper_raises(self):
        self.assertRaises(ValueError, nacl.helper.input_wrapper)

    @mock.patch('__builtin__.raw_input', return_value='answer')
    def test_input_wrapper_answer_given_1(self, mock_input):
        self.assertEqual('answer', nacl.helper.input_wrapper('Question'))

    @mock.patch('__builtin__.raw_input', return_value='answer')
    def test_input_wrapper_answer_given_2(self, mock_input):
        self.assertEqual('answer',
                         nacl.helper.input_wrapper('Question', 'default'))

    @mock.patch('__builtin__.raw_input', return_value=u'')
    def test_input_wrapper_stdout_no_input(self, mock_input):
        """ No input given but a default is present """
        self.assertEqual('default', nacl.helper.input_wrapper('Question', 'default'))

    @mock.patch('__builtin__.raw_input', return_value='answer')
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_input_wrapper_stdout_default(self, mock_stdout, mock_input):
        """ Patch sys.stdout to get the output under test """
        nacl.helper.input_wrapper('Question', 'Default')
        output = mock_stdout.getvalue()
        self.assertEqual(u'Question [\x1b[91mDefault\x1b[0m]:', output)

    @mock.patch('__builtin__.raw_input', return_value='answer')
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_input_wrapper_stdout_default_empty(self, mock_stdout, mock_input):
        """ Patch sys.stdout to get the output under test """
        nacl.helper.input_wrapper('Question', u'')
        output = mock_stdout.getvalue()
        self.assertEqual(u'Question:', output)

    @mock.patch('__builtin__.raw_input', return_value='answer')
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_input_wrapper_stdout_non_default(self, mock_stdout, mock_input):
        """ Patch sys.stdout to get the output under test """
        nacl.helper.input_wrapper('Question')
        output = mock_stdout.getvalue()
        self.assertEqual(u'Question:', output)

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

    # check_string_to_int()
    def test_check_int_1(self):
        self.assertTrue(nacl.helper.check_string_to_int('1'))

    def test_check_int_1_1(self):
        self.assertTrue(nacl.helper.check_string_to_int('-1'))

    def test_check_int_2(self):
        self.assertTrue(nacl.helper.check_string_to_int(2))

    def test_check_int_3(self):
        self.assertFalse(nacl.helper.check_string_to_int('AA'))

if __name__ == '__main__':
    unittest.main()
