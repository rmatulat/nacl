#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Test the flow.py """

import unittest
import mock
import pprint
from nacl.flow import NaclFlow


class TestNaclFlow(unittest.TestCase):
    """ Testting the nacl-flow.py main components """

    def setUp(self):
        self.flow = NaclFlow()

    def raise_TypeError():
        raise TypeError('foo')

    # get_all_issues()
    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_issues',
                side_effect=raise_TypeError)
    @mock.patch('sys.exit', return_value=None)
    def test_get_all_issues_raises(self, mock, mock_sysexit):
        self.assertEqual(
            [('FAIL', 'Project ID not found. Is remote origin a gitlab repo? (foo)', 1)],
            self.flow.get_all_issues._fn(self.flow))

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_issues',
                return_value=None)
    def test_get_all_issues_no_issues(self, mock):
        self.assertEqual(
            [('INFO', 'No issues found')],
            self.flow.get_all_issues._fn(self.flow))

    # some fake issues

    issues_open = [{
        'state': 'open',
        'title': 'foo',
        'iid': 123,
        'description': 'baz',
        'author': {'name': 'john doe'},
        'assignee': None
    }]

    issues_closed = [{
        'state': 'closed',
        'title': 'foo',
        'iid': 123,
        'description': 'baz',
        'author': {'name': 'john doe'},
        'assignee': None
    }]

    issues_assignee = [{
        'state': 'open',
        'title': 'foo',
        'iid': 123,
        'description': 'baz',
        'author': {'name': 'john doe'},
        u'assignee': {u'name': 'jane doe'}
    }]

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_issues',
                return_value=issues_open)
    def test_get_all_issues_issue_open(self, mock):
        self.assertEqual(
            [('INFO', 'TITLE: foo'),
             ('GREEN', 'ID: 123'),
             ('GREEN', 'WHAT: baz'),
             ('GREEN', 'STATE: open'),
             ('INFO', 'AUTHOR: john doe'),
             ('INFO', '--------------------------------------------------------------------------------')],
            self.flow.get_all_issues._fn(self.flow))

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_issues',
                return_value=issues_closed)
    def test_get_all_issues_issue_closed(self, mock):
        self.assertEqual([], self.flow.get_all_issues._fn(self.flow))

    @mock.patch('nacl.gitlabapi.GitLapApiCall.get_all_issues',
                return_value=issues_assignee)
    def test_get_all_issues_issue_assingnee(self, mock):
        self.assertEqual(
            [('INFO', 'TITLE: foo'),
             ('GREEN', 'ID: 123'),
             ('GREEN', 'WHAT: baz'),
             ('GREEN', 'STATE: open'),
             ('INFO', 'AUTHOR: john doe'),
             ('INFO', 'ASSIGNEE: jane doe'),
             ('INFO', '--------------------------------------------------------------------------------')],
            self.flow.get_all_issues._fn(self.flow))

    # get_my_issues()

if __name__ == '__main__':
    unittest.main()
