# -*- coding: utf-8 -*-
# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest

from mock import patch, Mock
from wazo_confgend.generators.queues import QueuesConf
from wazo_confgend.generators.tests.util import assert_generates_config


class TestQueuesConf(unittest.TestCase):
    def setUp(self):
        self.queues_conf = QueuesConf()

    @patch(
        'xivo_dao.asterisk_conf_dao.find_queue_penalty_settings', Mock(return_value=[])
    )
    @patch('xivo_dao.asterisk_conf_dao.find_queue_settings', Mock(return_value=[]))
    @patch(
        'xivo_dao.asterisk_conf_dao.find_queue_general_settings', Mock(return_value=[])
    )
    @patch(
        'xivo_dao.asterisk_conf_dao.find_queue_members_settings', Mock(return_value=[])
    )
    def test_empty_sections(self):
        assert_generates_config(
            self.queues_conf,
            '''
            [general]
        ''',
        )

    @patch(
        'xivo_dao.asterisk_conf_dao.find_queue_members_settings', Mock(return_value=[])
    )
    @patch(
        'xivo_dao.asterisk_conf_dao.find_queue_penalty_settings', Mock(return_value=[])
    )
    @patch('xivo_dao.asterisk_conf_dao.find_queue_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_queue_general_settings')
    def test_general_section(self, find_queue_general_settings):
        find_queue_general_settings.return_value = [
            {'var_name': 'autofill', 'var_val': 'no'},
        ]

        assert_generates_config(
            self.queues_conf,
            '''
            [general]
            autofill = no
        ''',
        )
        find_queue_general_settings.assert_called_once_with()

    @patch(
        'xivo_dao.asterisk_conf_dao.find_queue_penalty_settings', Mock(return_value=[])
    )
    @patch(
        'xivo_dao.asterisk_conf_dao.find_queue_general_settings', Mock(return_value=[])
    )
    @patch('xivo_dao.asterisk_conf_dao.find_queue_settings')
    @patch('xivo_dao.asterisk_conf_dao.find_queue_members_settings')
    def test_queues_section(self, find_queue_members_settings, find_queue_settings):
        find_queue_settings.return_value = [
            {
                'name': 'grp-supertenant-42f6b00e-0181-427b-b885-cf0b95893762',
                'label': 'group 1',
                'wrapuptime': 0,
                'joinempty': '',
                'leaveempty': '',
            }
        ]
        find_queue_members_settings.return_value = [
            ('PJSIP/abc', '1', '', ''),
            ('iface', '2', 'name', 'state_iface'),
        ]

        assert_generates_config(
            self.queues_conf,
            '''
            [general]

            ; group 1
            [grp-supertenant-42f6b00e-0181-427b-b885-cf0b95893762]
            wrapuptime = 0
            member = PJSIP/abc,1,,
            member = iface,2,name,state_iface
        ''',
        )
        find_queue_settings.assert_called_once_with()
        find_queue_members_settings.assert_called_once_with(
            'grp-supertenant-42f6b00e-0181-427b-b885-cf0b95893762'
        )
