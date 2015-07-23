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

import unittest

from mock import patch, Mock
from xivo_confgen.generators.queues import QueuesConf
from xivo_confgen.generators.tests.util import assert_generates_config


class TestQueuesConf(unittest.TestCase):

    def setUp(self):
        self.queues_conf = QueuesConf()

    @patch('xivo_dao.asterisk_conf_dao.find_queue_penalty_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_general_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_members_settings', Mock(return_value=[]))
    def test_empty_sections(self):
        assert_generates_config(self.queues_conf, '''
            [general]
        ''')

    @patch('xivo_dao.asterisk_conf_dao.find_queue_members_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_penalty_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_general_settings')
    def test_general_section(self, find_queue_general_settings):
        find_queue_general_settings.return_value = [
            {'var_name': 'autofill', 'var_val': 'no'},
        ]

        assert_generates_config(self.queues_conf, '''
            [general]
            autofill = no
        ''')
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

        assert_generates_config(self.queues_conf, '''
            [general]

            [queue1]
            wrapuptime = 0
            member => SIP/abc,1
        ''')
        find_queue_settings.assert_called_once_with()
        find_queue_members_settings.assert_called_once_with('queue1')
