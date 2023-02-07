# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest

from unittest.mock import Mock
from io import StringIO

from wazo_confgend.generators.tests.util import assert_config_equal

from ..asterisk import AsteriskFileGenerator


class TestConfBridgeConf(unittest.TestCase):
    def setUp(self):
        self.asterisk_file_dao = Mock()
        self.asterisk_file_generator = AsteriskFileGenerator(self.asterisk_file_dao)
        self.output = StringIO()

    def test_generate_file_when_not_found(self):
        file_ = None
        self.asterisk_file_generator._generate_file(file_, self.output)

        assert_config_equal(
            self.output.getvalue(),
            '''
        ''',
        )

    def test_generate_file(self):
        default_section = Mock(
            variables=[
                Mock(key='type', value='user'),
                Mock(key='max_members', value='50'),
            ]
        )
        default_section.name = 'default'
        general_section = Mock(variables=[])
        general_section.name = 'general'
        bridge1_section = Mock(
            variables=[
                Mock(key='record_conference', value='yes'),
                Mock(key='toto', value=None),
            ]
        )
        bridge1_section.name = 'bridge-1'
        file_ = Mock(
            sections_ordered=[
                general_section,
                default_section,
                bridge1_section,
            ]
        )
        self.asterisk_file_generator._generate_file(file_, self.output)

        assert_config_equal(
            self.output.getvalue(),
            '''
            [general]

            [default]
            type = user
            max_members = 50

            [bridge-1]
            record_conference = yes
            toto =
        ''',
        )
