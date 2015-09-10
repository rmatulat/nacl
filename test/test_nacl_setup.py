#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
import pprint
from io import StringIO
from nacl.setup import setup_git
from nacl.setup import setup_nacl
from nacl.exceptions import GitCallError


class TestNaclSetup(unittest.TestCase):

    # setup_git()

    @mock.patch('nacl.git.get_user_name', return_value='John Doe')
    @mock.patch('nacl.git.get_user_email', return_value='john@doe.com')
    @mock.patch('nacl.helper.input_wrapper', side_effect=['Jane', 'j@d.com'])
    @mock.patch('nacl.git.set_user_name', return_value=None)
    @mock.patch('nacl.git.set_user_email', return_value=None)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_setup_git_1(self,
                         mock_stdout,
                         mock_set_mail,
                         mock_set_name,
                         mock_wrapper,
                         mock_get_mail,
                         mock_get_name):
        self.assertTrue(setup_git())

    @mock.patch('nacl.git.get_user_name', return_value='John Doe')
    @mock.patch('nacl.git.get_user_email', return_value='john@doe.com')
    @mock.patch('nacl.helper.input_wrapper', return_value='Foo')
    @mock.patch('nacl.git.set_user_name', return_value=None)
    @mock.patch('nacl.git.set_user_email', return_value=None)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_setup_git_2(self,
                         mock_stdout,
                         mock_set_mail,
                         mock_set_name,
                         mock_wrapper,
                         mock_get_mail,
                         mock_get_name):
        setup_git()
        output = mock_stdout.getvalue()
        self.assertEqual(u'Git preferences updated to: \n\x1b[94mJohn Doe\x1b[0m\n\x1b[91mjohn@doe.com\x1b[0m\n', output)

    @mock.patch('nacl.git.get_user_name', return_value='John Doe')
    @mock.patch('nacl.git.get_user_email', return_value='john@doe.com')
    @mock.patch('nacl.helper.input_wrapper', return_value='Foo')
    @mock.patch('nacl.git.set_user_name', side_effect=GitCallError('Foo'))
    @mock.patch('nacl.git.set_user_email', return_value=None)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_setup_git_3(self,
                         mock_stdout,
                         mock_set_mail,
                         mock_set_name,
                         mock_wrapper,
                         mock_get_mail,
                         mock_get_name):

        setup_git()
        output = mock_stdout.getvalue()
        self.assertEqual(u'Something went wrong: Foo', output)

    # setup_nacl()

    def test_setup_nacl_1(self):
        self.assertTrue(setup_nacl())
