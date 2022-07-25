# -*- coding: utf-8 -*-
# Copyright 2011-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import unittest
import textwrap
from StringIO import StringIO

from hamcrest import assert_that, contains_string
from mock import Mock, patch
from xivo_dao.alchemy.ivr import IVR

from wazo_confgend.generators.extensionsconf import ExtensionsConf
from wazo_confgend.hints.generator import HintGenerator
from wazo_confgend.template import TemplateHelper
from jinja2.loaders import DictLoader


class TestExtensionsConf(unittest.TestCase):

    def setUp(self):
        self.hint_generator = Mock(HintGenerator)
        self.tpl_mapping = {}
        self.tpl_helper = TemplateHelper(DictLoader(self.tpl_mapping))
        self.extensionsconf = ExtensionsConf(
            'etc/wazo-confgend/templates/contexts.conf', self.hint_generator, self.tpl_helper
        )
        self.output = StringIO()
        self.maxDiff = 10000

    def test_generate_dialplan_from_template(self):
        template = ["%%EXTEN%%,%%PRIORITY%%,Set('__XIVO_BASE_CONTEXT': ${CONTEXT})"]
        exten = {'exten': '*98', 'priority': 1}
        self.extensionsconf.gen_dialplan_from_template(template, exten, self.output)

        self.assertEqual(self.output.getvalue(), "exten = *98,1,Set('__XIVO_BASE_CONTEXT': ${CONTEXT})\n\n")

    def test_generate_hints(self):
        hints = [
            'exten = 1000,hint,SIP/abcdef',
            'exten = 4000,hint,confbridge:1',
            'exten = *7351***223*1234,hint,Custom:*7351***223*1234',
        ]

        self.hint_generator.generate.return_value = hints

        self.extensionsconf._generate_hints('context', self.output)

        self.hint_generator.generate.assert_called_once_with('context')
        for hint in hints:
            self.assertTrue(hint in self.output.getvalue())

    @patch('wazo_confgend.generators.extensionsconf.ivr_dao')
    def test_generate_ivrs(self, mock_ivr_dao):
        ivr = IVR(id=42, name='foo', menu_sound=u'héllo-world')
        mock_ivr_dao.find_all_by.return_value = [ivr]
        self.tpl_mapping['asterisk/extensions/ivr.jinja'] = textwrap.dedent('''
            [xivo-ivr-{{ ivr.id }}]
            same  =   n,Background({{ ivr.menu_sound }})
        ''')

        self.extensionsconf._generate_ivr(self.output)

        assert_that(self.output.getvalue(), contains_string('[xivo-ivr-42]'))
        assert_that(self.output.getvalue(), contains_string(u'same  =   n,Background(héllo-world)'))

    @patch('wazo_confgend.generators.extensionsconf.ivr_dao')
    @patch('wazo_confgend.generators.extensionsconf.asterisk_conf_dao')
    def test_generate(self, mock_asterisk_conf_dao, mock_ivr_dao):
        hints = [
            'exten = 1000,hint,SIP/abcdef',
            'exten = 4000,hint,confbridge:1',
            'exten = *7351***223*1234,hint,Custom:*7351***223*1234',
        ]
        self.hint_generator.generate_global_hints.return_value = hints
        self.hint_generator.generate.return_value = hints

        mock_asterisk_conf_dao.find_extenfeatures_settings.return_value = [
            Mock(typeval="fwdbusy", exten="foo", commented=0),
            Mock(typeval="fwdrna", exten="bar", commented=1),
            Mock(typeval="fwdunc", exten="bar", commented=1),
        ]
        self.tpl_mapping['asterisk/extensions/ivr.jinja'] = "[xivo-ivr-{{ ivr.id }}]"

        mock_ivr_dao.find_all_by.return_value = [
            IVR(id=42, name='foo', menu_sound='hello-world'),
            IVR(id=43, name='bar', menu_sound='youhou'),
        ]

        mock_asterisk_conf_dao.find_context_settings.return_value = [
            {"name": "ctx_name", "contexttype": "incall", "tenant_uuid": "tenant-uuid"}
        ]
        mock_asterisk_conf_dao.find_contextincludes_settings.return_value = [
            {"include": "include-me.conf"}
        ]
        mock_asterisk_conf_dao.find_exten_settings.return_value = [
            {"type": "incall", "context": "default", "exten": "foo@bar", "typeval":
             "incallfilter", "id": 1234, "tenant_uuid": "2b853b5b-6c19-4123-90da-3ce05fe9aa74"},
        ]

        self.extensionsconf.generate(self.output)

        lines = [line for line in self.output.getvalue().split("\n") if line]
        path = os.path.dirname(__file__)
        with open(os.path.join(path, "expected_generated_extension.conf")) as f:
            expected_lines = [line for line in f.read().split("\n") if line]
        self.assertEqual(expected_lines, lines)
