# -*- coding: utf-8 -*-

# Copyright (C) 2011-2013 Avencall
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

from StringIO import StringIO
from mock import Mock
from xivo_confgen.generators.extensionsconf import ExtensionsConf
import unittest
from xivo import xivo_helpers


class TestExtensionsConf(unittest.TestCase):

    def assertConfigEqual(self, configExpected, configResult):
        self.assertEqual(configExpected.replace(' ', ''), configResult.replace(' ', ''))

    def setUp(self):
        self.extensionsconf = ExtensionsConf(None, 'context.conf')

    def tearDown(self):
        pass

    def test_generate_dialplan_from_template(self):
        output = StringIO()
        template = ["%%EXTEN%%,%%PRIORITY%%,Set('XIVO_BASE_CONTEXT': ${CONTEXT})"]
        exten = {'exten':'*98', 'priority':1}
        self.extensionsconf.gen_dialplan_from_template(template, exten, output)

        self.assertEqual(output.getvalue(), "exten = *98,1,Set('XIVO_BASE_CONTEXT': ${CONTEXT})\n\n")

    def test_generate_voice_menus(self):
        output = StringIO()
        voicemenus = [{'name': u'menu1',
                       },
                      {'name': u'menu2',
                       }
                      ]

        self.extensionsconf.backend = Mock()
        self.extensionsconf.backend.extensions.all.return_value = \
            [{'exten':u'2300', 'app':u'GoSub', 'priority':1, 'appdata':u'    endcall,s,1(hangup)'}]
        self.extensionsconf.generate_voice_menus(voicemenus, output)

        self.assertConfigEqual("""\
                                        [voicemenu-menu1]
                                        exten=2300,1,GoSub(endcall,s,1(hangup))
                                        
                                        [voicemenu-menu2]
                                        exten=2300,1,GoSub(endcall,s,1(hangup))
                                        
                                        """, output.getvalue())

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

    def test_prog_funckeys(self):
        keys = [{'exten': '1234',
                 'iduserfeatures': 2,
                 'leftexten': '*31'},
                {'exten': None,
                 'typevalextenumbersright': '20',
                 'iduserfeatures': 3,
                 'leftexten': '*21'}]
        keyfeature = Mock()
        keyfeature.get.return_value = '**432'
        xfeatures = {'phoneprogfunckey': keyfeature}
        def side_effect(exten, uplet):
            return exten + str(uplet[0]) + str(uplet[1]) + str(uplet[2])

        xivo_helpers.fkey_extension = side_effect
        self.extensionsconf.backend = Mock()
        self.extensionsconf.backend.progfunckeys.all.return_value = keys

        result = self.extensionsconf._prog_funckeys({'name': 'default'}, xfeatures)

        expected_result = '''
; prog funckeys supervision
exten = **4322*311234,hint,Custom:**4322*311234
exten = **4323*21*20,hint,Custom:**4323*21*20
'''

        self.assertEquals(expected_result, result)
