# Copyright 2011-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest
from unittest.mock import Mock, patch

from wazo_confgend.asterisk import AsteriskFrontend
from wazo_confgend.generators.tests.util import assert_config_equal


class Test(unittest.TestCase):
    def setUp(self):
        self._config = {
            'templates': {'contextsconf': None},
        }
        self.tpl_helper = Mock()
        self.asteriskFrontEnd = AsteriskFrontend(self._config, self.tpl_helper)

    @patch('xivo_dao.asterisk_conf_dao.find_agent_queue_skills_settings')
    def test_queueskills_conf(self, find_agent_queue_skills_settings):
        find_agent_queue_skills_settings.return_value = [
            {'id': 1, 'name': 'test-skill', 'weight': 10},
        ]
        assert_config_equal(
            self.asteriskFrontEnd.queueskills_conf(),
            """
            [agent-1]
            test-skill = 10
            """,
        )
        find_agent_queue_skills_settings.assert_called_once_with()

    @patch('xivo_dao.asterisk_conf_dao.find_queue_skillrule_settings')
    def test_queueskillrules_conf(self, find_queue_skillrule_settings):
        find_queue_skillrule_settings.return_value = [
            {'id': 1, 'name': 'test-rule-1', 'rule': 'rule-1;rule-2'},
            {'id': 2, 'name': 'test-rule-2', 'rule': 'rule-3;rule-4'},
        ]
        assert_config_equal(
            self.asteriskFrontEnd.queueskillrules_conf(),
            """
            [skillrule-1]
            rule = rule-1
            rule = rule-2

            [skillrule-2]
            rule = rule-3
            rule = rule-4
            """,
        )
        find_queue_skillrule_settings.assert_called_once_with()

    @patch('xivo_dao.asterisk_conf_dao.find_queue_penalties_settings')
    def test_queuerules_conf(self, find_queue_penalties_settings):
        find_queue_penalties_settings.return_value = [
            {
                'name': 'rule-1',
                'seconds': 25,
                'maxp_sign': '=',
                'maxp_value': 2,
                'minp_sign': '+',
                'minp_value': 2,
            },
            {'name': 'rule-2', 'seconds': 30, 'maxp_sign': None, 'minp_sign': None},
        ]
        assert_config_equal(
            self.asteriskFrontEnd.queuerules_conf(),
            """
            [rule-1]
            penaltychange => 252,+2
            [rule-2]
            penaltychange => 30
            """,
        )
        find_queue_penalties_settings.assert_called_once_with()
