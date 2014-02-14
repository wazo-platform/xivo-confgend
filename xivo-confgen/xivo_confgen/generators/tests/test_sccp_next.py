# -*- coding: utf-8 -*-

# Copyright (C) 2011-2014 Avencall
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

import StringIO
import unittest
from mock import Mock, patch

from xivo_confgen.generators.sccp_next import SccpNextConf, _SccpGeneralSettingsConf, _SccpLineConf, _SccpDeviceConf, \
    _SccpSpeedDialConf


class _BaseSccpTestCase(unittest.TestCase):

    def assertConfigEqual(self, configExpected, configResult):
        self.assertEqual(configExpected.replace(' ', ''), configResult.replace(' ', ''))


class TestSccpNextConf(_BaseSccpTestCase):

    @patch('xivo_dao.asterisk_conf_dao.find_sccp_general_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_line_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_device_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_speeddial_settings', Mock(return_value=[]))
    def setUp(self):
        self._output = StringIO.StringIO()
        self.sccp_conf = SccpNextConf()

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
                    [1229-1]
                    type = speeddial
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
        sccp_conf._generate_devices(sccpdevice, self._output)

        expected = """\
                    [SEPACA016FDF235](xivo_device_tpl)
                    type=device
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
        sccp_conf._generate_devices(sccpdevice, self._output)

        expected = """\
                    [SEPACA016FDF235](xivo_device_tpl)
                    type=device

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
        sccp_conf._generate_devices(sccpdevice, self._output)

        expected = """\
                    [SEPACA016FDF235](xivo_device_tpl)
                    type=device
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
        items = [{'option_name': u'foo',
                  'option_value': u'bar'}]

        self._general_conf.generate(items, self._output)

        expected = """\
                    [general]
                    foo=bar

                   """
        self.assertConfigEqual(expected, self._output.getvalue())


class TestSccpLineConf(_BaseSccpTestCase):

    def setUp(self):
        self._line_conf = _SccpLineConf()
        self._output = StringIO.StringIO()

    def test_template_allow_option(self):
        items = [
            {'option_name': 'allow', 'option_value': 'ulaw'},
        ]

        self._line_conf._generate_template(items, self._output)

        expected = """\
                   [xivo_line_tpl](!)
                   disallow = all
                   allow = ulaw

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_template_empty_allow_option(self):
        items = [
            {'option_name': 'allow', 'option_value': ''},
        ]

        self._line_conf._generate_template(items, self._output)

        expected = """\
                   [xivo_line_tpl](!)

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

    def test_template_disallow_option_is_ignored(self):
        items = [
            {'option_name': 'disallow', 'option_value': 'foobar'},
        ]

        self._line_conf._generate_template(items, self._output)

        expected = """\
                   [xivo_line_tpl](!)

                   """
        self.assertConfigEqual(expected, self._output.getvalue())

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

        self._line_conf._generate_lines(sccpline, self._output)

        expected = """\
                    [100](xivo_line_tpl)
                    type=line
                    cid_name=jimmy
                    cid_num=100
                    setvar=XIVO_USERID=1
                    setvar=PICKUPMARK=100%a_context
                    setvar=TRANSFER_CONTEXT=a_context
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

        self._line_conf._generate_lines(sccpline, self._output)

        expected = """\
                    [100](xivo_line_tpl)
                    type=line
                    cid_name=jimmy
                    cid_num=100
                    setvar=XIVO_USERID=1
                    setvar=PICKUPMARK=100%a_context
                    setvar=TRANSFER_CONTEXT=a_context
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

        self._line_conf._generate_lines(sccpline, self._output)

        expected = """\
                    [100](xivo_line_tpl)
                    type=line
                    cid_name=jimmy
                    cid_num=100
                    setvar=XIVO_USERID=1
                    setvar=PICKUPMARK=100%a_context
                    setvar=TRANSFER_CONTEXT=a_context
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

        self._line_conf._generate_lines(sccpline, self._output)

        expected = """\
                    [100](xivo_line_tpl)
                    type=line
                    cid_name=jimmy
                    cid_num=100
                    setvar=XIVO_USERID=1
                    setvar=PICKUPMARK=100%a_context
                    setvar=TRANSFER_CONTEXT=a_context
                    context=a_context
                    disallow=all
                    allow=g729,ulaw

                   """
        self.assertConfigEqual(expected, self._output.getvalue())
