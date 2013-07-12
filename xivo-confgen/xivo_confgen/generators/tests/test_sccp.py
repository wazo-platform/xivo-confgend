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

import os
import StringIO
import unittest
import mock
from xivo_confgen.generators.sccp import SccpConf, _SccpGeneralSettingsConf, _SccpLineConf, _SccpDeviceConf, \
    _SccpSpeedDialConf
from xivo_confgen.generators.tests.util import parse_ast_config


class TestSccpConf(unittest.TestCase):
    def setUp(self):
        self._output = StringIO.StringIO()

    def _parse_ast_cfg(self):
        self._output.seek(os.SEEK_SET)
        return parse_ast_config(self._output)

    def assertConfigEqual(self, configExpected, configResult):
        self.assertEqual(configExpected.replace(' ', ''), configResult.replace(' ', ''))

    def test_empty_sections(self):
        sccp_conf = SccpConf([], [], [], [])
        sccp_conf.generate(self._output)

        result = self._parse_ast_cfg()
        expected = {u'general': [],
                    u'devices': [],
                    u'lines': [],
                    u'speeddials': []}

        self.assertEqual(expected, result)

    def test_one_element_general_section(self):
        sccpgeneralsettings = [{'option_name': u'foo',
                                'option_value': u'bar'}]

        sccp_conf = _SccpGeneralSettingsConf()
        sccp_conf.generate(sccpgeneralsettings, self._output)

        expected = """\
                    [general]
                    foo=bar

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_one_element_lines_section(self):
        sccpline = [{'category': u'lines',
                     'name': u'100',
                     'cid_name': u'jimmy',
                     'cid_num': u'100',
                     'user_id': u'1',
                     'language': u'fr_FR',
                     'number': 100,
                     'context': u'a_context'}]

        sccp_conf = _SccpLineConf()
        sccp_conf.generate(sccpline, self._output)

        expected = """\
                    [lines]
                    [100]
                    cid_name=jimmy
                    cid_num=100
                    setvar=XIVO_USERID=1
                    setvar=PICKUPMARK=100%a_context
                    language=fr_FR
                    context=a_context

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_one_element_lines_section_no_language(self):
        sccpline = [{'category': u'lines',
                     'name': u'100',
                     'cid_name': u'jimmy',
                     'cid_num': u'100',
                     'user_id': u'1',
                     'language': None,
                     'number': 100,
                     'context': u'a_context'}]

        sccp_conf = _SccpLineConf()
        sccp_conf.generate(sccpline, self._output)

        expected = """\
                    [lines]
                    [100]
                    cid_name=jimmy
                    cid_num=100
                    setvar=XIVO_USERID=1
                    setvar=PICKUPMARK=100%a_context
                    context=a_context

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_one_element_speeddials_section(self):
        speedials = [{'exten':'1001',
                      'fknum': 1,
                      'label': 'user001',
                      'supervision': 0,
                      'iduserfeatures': 1229,
                      'number': '103',
                      'device': 'SEPACA016FDF235'}]

        sccp_conf = _SccpSpeedDialConf()
        sccp_conf.generate(speedials, self._output)

        expected = """\
                    [speeddials]
                    [1229-1]
                    extension = 1001
                    label = user001
                    blf = 0

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_one_element_devices_section(self):
        sccpdevice = [{'category': u'devices',
                       'name': u'SEPACA016FDF235',
                       'device': u'SEPACA016FDF235',
                       'line': u'103',
                       'voicemail': u'103'}]

        sccpspeeddials = [{'exten':'1001',
                           'fknum': 1,
                           'label': 'user001',
                           'supervision': 0,
                           'iduserfeatures': 1229,
                           'number': '103',
                           'device': 'SEPACA016FDF235'}]

        sccp_conf = _SccpDeviceConf(sccpspeeddials)
        sccp_conf.generate(sccpdevice, self._output)

        expected = """\
                    [devices]
                    [SEPACA016FDF235]
                    device=SEPACA016FDF235
                    line=103
                    voicemail=103
                    speeddial=1229-1

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_one_device_no_line_no_voicemail(self):
        sccpdevice = [{'category': u'devices',
                       'name': u'SEPACA016FDF235',
                       'device': u'SEPACA016FDF235',
                       'line': u'',
                       'voicemail': u''}]

        sccp_conf = _SccpDeviceConf([])
        sccp_conf.generate(sccpdevice, self._output)

        expected = """\
                    [devices]
                    [SEPACA016FDF235]
                    device=SEPACA016FDF235

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_general_section(self):
        sccp = [{'option_name': u'bindaddr',
                 'option_value': u'0.0.0.0'},
                {'option_name': u'dateformat',
                 'option_value': u'D.M.Y'},
                {'option_name': u'keepalive',
                 'option_value': u'10'},
                {'option_name': u'authtimeout',
                 'option_value': u'10'}]

        sccp_conf = SccpConf(sccp, [], [], [])
        sccp_conf.generate(self._output)

        result = self._parse_ast_cfg()
        expected = {u'general': [u'bindaddr = 0.0.0.0',
                                 u'dateformat = D.M.Y',
                                 u'keepalive = 10',
                                 u'authtimeout = 10'],
                    u'lines': [],
                    u'devices': [],
                    u'speeddials': []}

        self.assertEqual(expected, result)

    def test_new_from_backend(self):
        backend = mock.Mock()
        SccpConf.new_from_backend(backend)
        backend.sccpgeneralsettings.all.assert_called_once_with()
        backend.sccpline.all.assert_called_once_with()
        backend.sccpdevice.all.assert_called_once_with()
        backend.sccpspeeddial.all.assert_called_once_with()

    def test_multiple_speedials_devices_section(self):
        sccpdevice = [{'category': u'devices',
                       'name': u'SEPACA016FDF235',
                       'device': u'SEPACA016FDF235',
                       'line': u'103',
                       'voicemail': u'103'}]

        sccpspeeddials = [
            {'exten':'1002',
             'fknum': 2,
             'label': 'user002',
             'supervision': 0,
             'iduserfeatures': 1229,
             'number': '103',
             'device': 'SEPACA016FDF235'},
            {'exten':'1001',
             'fknum': 1,
             'label': 'user001',
             'supervision': 0,
             'iduserfeatures': 1229,
             'number': '103',
             'device': 'SEPACA016FDF235'},
        ]

        sccp_conf = _SccpDeviceConf(sccpspeeddials)
        sccp_conf.generate(sccpdevice, self._output)

        expected = """\
                    [devices]
                    [SEPACA016FDF235]
                    device=SEPACA016FDF235
                    line=103
                    voicemail=103
                    speeddial=1229-1
                    speeddial=1229-2

                   """
        self.assertConfigEqual(expected, self._output.getvalue())
