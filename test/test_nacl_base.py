#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from nacl.fileutils import get_salt_root_dirs


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


if __name__ == '__main__':
    unittest.main()
