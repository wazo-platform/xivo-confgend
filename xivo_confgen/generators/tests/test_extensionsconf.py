# -*- coding: utf-8 -*-

# Copyright (C) 2011-2014 Avencall
# Copyright (C) 2016 Proformatique Inc.
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
from StringIO import StringIO

from hamcrest import assert_that, contains_string
from mock import Mock, patch
from xivo_dao.alchemy.ivr import IVR

from xivo_confgen.generators.extensionsconf import ExtensionsConf
from xivo_confgen.hints.generator import HintGenerator
from xivo_confgen.template import TemplateHelper
from jinja2.loaders import DictLoader


class TestExtensionsConf(unittest.TestCase):

    def setUp(self):
        self.hint_generator = Mock(HintGenerator)
        self.tpl_mapping = {}
        self.tpl_helper = TemplateHelper(DictLoader(self.tpl_mapping))
        self.extensionsconf = ExtensionsConf('context.conf', self.hint_generator, self.tpl_helper)
        self.output = StringIO()

    def test_generate_dialplan_from_template(self):
        template = ["%%EXTEN%%,%%PRIORITY%%,Set('XIVO_BASE_CONTEXT': ${CONTEXT})"]
        exten = {'exten': '*98', 'priority': 1}
        self.extensionsconf.gen_dialplan_from_template(template, exten, self.output)

        self.assertEqual(self.output.getvalue(), "exten = *98,1,Set('XIVO_BASE_CONTEXT': ${CONTEXT})\n\n")

    def test_bsfilter_build_extens(self):
        bs1 = {'bsfilter': 'boss',
               'exten': 1001,
               'number': 1000}
        query_result = [bs1]

        result = self.extensionsconf._build_sorted_bsfilter(query_result)

        expected = set([(1000, 1001)])

        self.assertEqual(result, expected)

    def test_bsfilter_build_extend_no_double(self):
        bs1 = {'bsfilter': 'boss',
               'exten': 1001,
               'number': 1000}
        bs2 = {'bsfilter': 'secretary',
               'exten': 1000,
               'number': 1001}
        query_result = [bs1, bs2]

        result = self.extensionsconf._build_sorted_bsfilter(query_result)

        expected = set([(1000, 1001)])

        self.assertEqual(result, expected)

    def test_bsfilter_build_extend_no_two_secretaries(self):
        bs1 = {'bsfilter': 'boss',
               'exten': 1001,
               'number': 1000}
        bs2 = {'bsfilter': 'secretary',
               'exten': 1000,
               'number': 1001}
        bs3 = {'bsfilter': 'boss',
               'exten': 1002,
               'number': 1000}
        bs4 = {'bsfilter': 'secretary',
               'exten': 1000,
               'number': 1002}
        query_result = [bs1, bs2, bs3, bs4]

        result = self.extensionsconf._build_sorted_bsfilter(query_result)

        expected = set([(1000, 1001), (1000, 1002)])

        self.assertEqual(result, expected)

    def test_generate_hints(self):
        hints = [
            'exten = 1000,hint,SIP/abcdef',
            'exten = 4000,hint,meetme:4000',
            'exten = *7351***223*1234,hint,Custom:*7351***223*1234',
        ]

        self.hint_generator.generate.return_value = hints

        self.extensionsconf._generate_hints('context', self.output)

        self.hint_generator.generate.assert_called_once_with('context')
        for hint in hints:
            self.assertTrue(hint in self.output.getvalue())

    @patch('xivo_confgen.generators.extensionsconf.ivr_dao')
    def test_generate_ivrs(self, mock_ivr_dao):
        ivr = IVR(id=42, name='foo', menu_sound='hello-world')
        mock_ivr_dao.find_all_by.return_value = [ivr]
        self.tpl_mapping['asterisk/extensions/ivr.jinja'] = '{{ ivr.id }}'

        self.extensionsconf._generate_ivr(self.output)

        assert_that(self.output.getvalue(), contains_string('42'))
