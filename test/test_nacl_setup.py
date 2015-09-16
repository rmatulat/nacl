#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
import pprint
from io import StringIO
from io import BytesIO
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
        """ test whether exception is catched """
        setup_git()
        output = mock_stdout.getvalue()
        self.assertEqual(u'Something went wrong: Foo', output)

    # setup_nacl()

    answer_list = [
        'http://test.example.com',
        'TestMyToken',
        'test_saltstack',
        'http://testproxy.com:8000',
        'ignore1.git, ignore2.git'
    ]

    @mock.patch('nacl.base.get_users_nacl_conf', return_value=None)
    @mock.patch('nacl.base.write_users_nacl_conf', return_value=True)
    @mock.patch('nacl.helper.input_wrapper', side_effect=answer_list)
    @mock.patch('nacl.helper.query_yes_no', return_value=True)
    @mock.patch('sys.stdout', new_callable=BytesIO)
    @mock.patch('sys.stderr', new_callable=BytesIO)
    def test_setup_nacl(self,
                        mock_stderr,
                        mock_stdout,
                        mock_yes_no,
                        mock_input,
                        mock_wunc,
                        mock_gunc):
        setup_nacl()
        output = mock_stdout.getvalue()
        self.assertEqual('\n.nacl file written\n', output)

    @mock.patch('nacl.base.get_users_nacl_conf', return_value=None)
    @mock.patch('nacl.base.write_users_nacl_conf', return_value=False)
    @mock.patch('nacl.helper.input_wrapper', side_effect=answer_list)
    @mock.patch('nacl.helper.query_yes_no', return_value=True)
    @mock.patch('sys.stdout', new_callable=BytesIO)
    @mock.patch('sys.stderr', new_callable=BytesIO)
    def test_setup_nacl_no_write(self,
                                 mock_stderr,
                                 mock_stdout,
                                 mock_yes_no,
                                 mock_input,
                                 mock_wunc,
                                 mock_gunc):
        setup_nacl()
        output = mock_stderr.getvalue()
        self.assertEqual('\nSomething went wrong!\n', output)

    # when a .nacl file is provided, but some values in it are missing,
    # then stop throwing KeyError.
    # In this case 'proxy' is missing.

    emulate_incomplete_nacl_file = {
        'gitapiserver': 'https://gitlab.example.com',
        'gitapitoken': '<MyAweSomeToken>',
        'gitgroup': 'saltstack',
        'ignore_repositories': [
            'git@gitlab.example.com:saltstack/example.git']
    }

    @mock.patch('nacl.base.get_users_nacl_conf',
                return_value=emulate_incomplete_nacl_file)
    @mock.patch('nacl.base.write_users_nacl_conf', return_value=True)
    @mock.patch('nacl.helper.input_wrapper', side_effect=answer_list)
    @mock.patch('nacl.helper.query_yes_no', return_value=True)
    @mock.patch('sys.stdout', new_callable=BytesIO)
    @mock.patch('sys.stderr', new_callable=BytesIO)
    def test_setup_nacl_no_keyerror(self,
                                    mock_stderr,
                                    mock_stdout,
                                    mock_yes_no,
                                    mock_input,
                                    mock_wunc,
                                    mock_gunc):
        setup_nacl()
        output = mock_stdout.getvalue()
        self.assertEqual('\n.nacl file written\n', output)