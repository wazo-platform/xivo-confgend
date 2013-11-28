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
from mock import Mock, patch

from xivo_confgen.generators.sccp import SccpConf, _SccpGeneralSettingsConf, _SccpLineConf, _SccpDeviceConf, \
    _SccpSpeedDialConf
from xivo_confgen.generators.tests.util import parse_ast_config


class _BaseSccpTestCase(unittest.TestCase):

    def assertConfigEqual(self, configExpected, configResult):
        self.assertEqual(configExpected.replace(' ', ''), configResult.replace(' ', ''))


class TestSccpConf(_BaseSccpTestCase):

    @patch('xivo_dao.asterisk_conf_dao.find_sccp_general_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_line_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_device_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_speeddial_settings', Mock(return_value=[]))
    def setUp(self):
        self._output = StringIO.StringIO()
        self.sccp_conf = SccpConf()

    def _parse_ast_cfg(self):
        self._output.seek(os.SEEK_SET)
        return parse_ast_config(self._output)

    @patch('xivo_dao.asterisk_conf_dao.find_sccp_general_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_line_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_device_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_speeddial_settings', Mock(return_value=[]))
    def test_empty_sections(self):
        sccp_conf = SccpConf()
        sccp_conf.generate(self._output)

        result = self._parse_ast_cfg()
        expected = {u'general': [],
                    u'devices': [],
                    u'lines': [],
                    u'speeddials': []}

        self.assertEqual(expected, result)

    def test_one_element_speeddials_section(self):
        speedials = [{'exten':'1001',
                      'fknum': 1,
                      'label': 'user001',
                      'supervision': 0,
                      'user_id': 1229,
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
                           'user_id': 1229,
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
             'user_id': 1229,
             'device': 'SEPACA016FDF235'},
            {'exten':'1001',
             'fknum': 1,
             'label': 'user001',
             'supervision': 0,
             'user_id': 1229,
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


class TestSccpGeneralConf(_BaseSccpTestCase):

    def setUp(self):
        self._general_conf = _SccpGeneralSettingsConf()
        self._output = StringIO.StringIO()

    def test_one_element_general_section(self):
        sccpgeneralsettings = [{'option_name': u'foo',
                                'option_value': u'bar'}]

        self._general_conf.generate(sccpgeneralsettings, self._output)

        expected = """\
                    [general]
                    foo=bar

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_allow_option(self):
        sccpgeneralsettings = [
            {'option_name': 'allow', 'option_value': 'ulaw'},
        ]

        self._general_conf.generate(sccpgeneralsettings, self._output)

        expected = """\
                   [general]
                   disallow = all
                   allow = ulaw

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_empty_allow_option(self):
        sccpgeneralsettings = [
            {'option_name': 'allow', 'option_value': ''},
        ]

        self._general_conf.generate(sccpgeneralsettings, self._output)

        expected = """\
                   [general]

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_disallow_option_is_ignored(self):
        sccpgeneralsettings = [
            {'option_name': 'disallow', 'option_value': 'foobar'},
        ]

        self._general_conf.generate(sccpgeneralsettings, self._output)

        expected = """\
                   [general]

                   """
        self.assertConfigEqual(expected, self._output.getvalue())


class TestSccpLineConf(_BaseSccpTestCase):

    def setUp(self):
        self._line_conf = _SccpLineConf()
        self._output = StringIO.StringIO()

    def test_one_element_lines_section(self):
        sccpline = [{
            'category': u'lines',
            'name': u'100',
            'cid_name': u'jimmy',
            'cid_num': u'100',
            'user_id': u'1',
            'language': u'fr_FR',
            'number': 100,
            'context': u'a_context',
        }]

        self._line_conf.generate(sccpline, self._output)

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
        sccpline = [{
            'category': u'lines',
            'name': u'100',
            'cid_name': u'jimmy',
            'cid_num': u'100',
            'user_id': u'1',
            'language': None,
            'number': 100,
            'context': u'a_context',
        }]

        self._line_conf.generate(sccpline, self._output)

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

    def test_allow_no_disallow(self):
        sccpline = [{
            'category': u'lines',
            'name': u'100',
            'cid_name': u'jimmy',
            'cid_num': u'100',
            'user_id': u'1',
            'language': None,
            'number': 100,
            'context': u'a_context',
            'allow': u'g729,ulaw',
        }]

        self._line_conf.generate(sccpline, self._output)

        expected = """\
                    [lines]
                    [100]
                    cid_name=jimmy
                    cid_num=100
                    setvar=XIVO_USERID=1
                    setvar=PICKUPMARK=100%a_context
                    context=a_context
                    allow=g729,ulaw

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_disallow_all_allow_order(self):
        sccpline = [{
            'category': u'lines',
            'name': u'100',
            'cid_name': u'jimmy',
            'cid_num': u'100',
            'user_id': u'1',
            'language': None,
            'number': 100,
            'context': u'a_context',
            'allow': u'g729,ulaw',
            'disallow': u'all',
        }]

        self._line_conf.generate(sccpline, self._output)

        expected = """\
                    [lines]
                    [100]
                    cid_name=jimmy
                    cid_num=100
                    setvar=XIVO_USERID=1
                    setvar=PICKUPMARK=100%a_context
                    context=a_context
                    disallow=all
                    allow=g729,ulaw

                   """
        self.assertConfigEqual(expected, self._output.getvalue())
