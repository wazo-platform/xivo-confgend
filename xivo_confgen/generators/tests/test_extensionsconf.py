# -*- coding: utf-8 -*-
# Copyright 2011-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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
