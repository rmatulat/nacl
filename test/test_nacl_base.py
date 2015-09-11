#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from nacl.base import get_salt_root_dirs
from nacl.base import get_users_nacl_conf
from nacl.base import init_nacl


class TestNaclBase(unittest.TestCase):

    # get_salt_root_dirs()

    sample_salt_config = {
        'pillar_roots': {
            'base': ['/srv/pillar/base'],
            'dev': ['/srv/pillar/dev'],
            'prod': ['/srv/pillar/prod']},
        'file_roots': {
            'base': ['/srv/salt/base'],
            'prod': ['/srv/salt/prod'
                     '/srv/formulas/nginx-formula']}}

    @mock.patch('salt.config.client_config', return_value=sample_salt_config)
    def test_get_salt_root_dir(self, mock_config):
        self.assertEqual(['/srv/pillar/base',
                          '/srv/pillar/dev',
                          '/srv/pillar/prod',
                          '/srv/salt/base',
                          '/srv/salt/prod/srv/formulas/nginx-formula'],
                         get_salt_root_dirs())

    # get_users_nacl_conf()

    @mock.patch('os.path.expanduser', return_value="/tmp/")
    @mock.patch('__builtin__.open')
    @mock.patch('json.load', return_value="{'foo': 'bar'}")
    def test_get_users_nacl_conf(self, os_mock, open_mock, json_mock):
        """ get_users_nacl_conf() works fine """
        self.assertEqual("{'foo': 'bar'}", get_users_nacl_conf())

    @mock.patch('os.path.expanduser', return_value="/tmp/")
    @mock.patch('__builtin__.open')
    @mock.patch('json.load', side_effect=ValueError())
    def test_get_users_nacl_conf_exception(self,
                                           os_mock,
                                           open_mock,
                                           json_mock):
        """ Catching an exception """
        self.assertEqual([('FAIL', ' ~/.nacl not found or invalid JSON', 3)],
                         get_users_nacl_conf._fn())

    @mock.patch('os.path.expanduser', return_value="/tmp/")
    @mock.patch('__builtin__.open')
    @mock.patch('json.load', side_effect=ValueError())
    def test_get_users_nacl_conf_no_logging(self,
                                            os_mock,
                                            open_mock,
                                            json_mock):
        """ Catching an exception, print no logs"""
        self.assertFalse(get_users_nacl_conf(True))

    # test the except block
    @mock.patch('os.path.expanduser', return_value="/tmp/")
    @mock.patch('__builtin__.open')
    @mock.patch('json.load', side_effect=TypeError())
    def test_get_users_nacl_conf_raises(self, os_mock, open_mock, json_mock):
        self.assertEqual([('FAIL', ' ~/.nacl not found or invalid JSON', 3)],
                         get_users_nacl_conf._fn())

    # init_nacl()
    def test_init_nacl(self):
        self.assertTrue(init_nacl())

if __name__ == '__main__':
    unittest.main()
