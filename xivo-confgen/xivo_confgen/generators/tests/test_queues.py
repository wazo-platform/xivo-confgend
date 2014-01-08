# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import StringIO
import unittest
from mock import patch, Mock
from xivo_confgen.generators.queues import QueuesConf
from xivo_confgen.generators.tests.util import build_expected


class TestQueuesConf(unittest.TestCase):

    def setUp(self):
        self.output = StringIO.StringIO()
        self.queues_conf = QueuesConf()

    @patch('xivo_dao.asterisk_conf_dao.find_queue_penalty_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_general_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_members_settings', Mock(return_value=[]))
    def test_empty_sections(self):
        self.queues_conf.generate(self.output)

        expected_output = build_expected('''\
            [general]
        ''')
        self.assertEqual(self.output.getvalue(), expected_output)

    @patch('xivo_dao.asterisk_conf_dao.find_queue_members_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_penalty_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_general_settings')
    def test_general_section(self, find_queue_general_settings):
        find_queue_general_settings.return_value = [
            {'var_name': 'autofill', 'var_val': 'no'},
        ]

        self.queues_conf.generate(self.output)

        expected_output = build_expected('''\
            [general]
            autofill = no
        ''')
        self.assertEqual(self.output.getvalue(), expected_output)
        find_queue_general_settings.assert_called_once_with()

    @patch('xivo_dao.asterisk_conf_dao.find_queue_penalty_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_general_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_settings')
    @patch('xivo_dao.asterisk_conf_dao.find_queue_members_settings')
    def test_queues_section(self, find_queue_members_settings, find_queue_settings):
        find_queue_settings.return_value = [
            {'name': 'queue1', 'wrapuptime': 0, 'commented': False, 'joinempty': '', 'leaveempty': u''}
        ]
        find_queue_members_settings.return_value = [
            {'interface': 'SIP/abc', 'penalty': 1, 'state_interface': '', 'skills': 'user-1'},
        ]

        self.queues_conf.generate(self.output)

        expected_output = build_expected('''\
            [general]

            [queue1]
            wrapuptime = 0
            member => SIP/abc,1
        ''')
        self.assertEqual(self.output.getvalue(), expected_output)
        find_queue_settings.assert_called_once_with()
        find_queue_members_settings.assert_called_once_with('queue1')
