# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016 Avencall
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

import itertools
import StringIO
import unittest

from mock import Mock, patch
from uuid import uuid4

from xivo_confgen.generators.tests.util import assert_generates_config,\
    assert_config_equal

from xivo_confgen.generators.sccp import SccpConf, _SccpGeneralSettingsConf, _SccpLineConf, _SccpDeviceConf, \
    _SccpSpeedDialConf, _SplittedGeneralSettings


class TestSccpConf(unittest.TestCase):

    @patch('xivo_dao.asterisk_conf_dao.find_sccp_general_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_line_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_device_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_sccp_speeddial_settings', Mock(return_value=[]))
    def setUp(self):
        self._output = StringIO.StringIO()
        self._conf = SccpConf()

    def test_generate(self):
        assert_generates_config(self._conf, '''
            [general]

            [xivo_device_tpl](!)

            [xivo_line_tpl](!)
        ''')

    def test_one_element_speeddials_section(self):
        speedials = [{'exten': '1001',
                      'fknum': 1,
                      'label': 'user001',
                      'supervision': 0,
                      'user_id': 1229,
                      'device': 'SEPACA016FDF235'}]

        sccp_conf = _SccpSpeedDialConf()
        sccp_conf.generate(speedials, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [1229-1]
            type = speeddial
            extension = 1001
            label = user001
            blf = 0
        ''')

    def test_speeddial_no_label(self):
        speedials = [{'exten': '1001',
                      'fknum': 1,
                      'label': None,
                      'supervision': 0,
                      'user_id': 1229,
                      'device': 'SEPACA016FDF235'}]

        sccp_conf = _SccpSpeedDialConf()
        sccp_conf.generate(speedials, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [1229-1]
            type = speeddial
            extension = 1001
            blf = 0
        ''')


class TestSccpGeneralConf(unittest.TestCase):

    def setUp(self):
        self._general_conf = _SccpGeneralSettingsConf()
        self._output = StringIO.StringIO()

    def test_one_element_general_section(self):
        items = [{'option_name': u'foo',
                  'option_value': u'bar'}]

        self._general_conf.generate(items, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [general]
            foo = bar
        ''')


class TestSccpSplittedGeneralSettings(unittest.TestCase):

    def test_split_options(self):
        general_items = [
            {'option_name': 'foo'},
        ]
        device_items = [
            {'option_name': 'keepalive'},
        ]
        line_items = [
            {'option_name': 'language'},
        ]
        items = list(itertools.chain(general_items, device_items, line_items))

        splitted_settings = _SplittedGeneralSettings.new_from_dao_general_settings(items)

        self.assertEqual(general_items, splitted_settings.general_items)
        self.assertEqual(device_items, splitted_settings.device_items)
        self.assertEqual(line_items, splitted_settings.line_items)


class TestSccpDeviceConf(unittest.TestCase):

    def setUp(self):
        self._device_conf = _SccpDeviceConf([])
        self._output = StringIO.StringIO()

    def test_template_items(self):
        items = [
            {'option_name': 'foo', 'option_value': 'bar'},
        ]

        self._device_conf._generate_template(items, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [xivo_device_tpl](!)
            foo = bar
        ''')

    def test_one_device_no_line_no_voicemail(self):
        sccpdevice = [{'category': u'devices',
                       'name': u'SEPACA016FDF235',
                       'device': u'SEPACA016FDF235',
                       'line': u'',
                       'voicemail': u''}]

        self._device_conf._generate_devices(sccpdevice, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [SEPACA016FDF235](xivo_device_tpl)
            type = device
        ''')

    def test_one_element_devices_section(self):
        sccpdevice = [{'category': u'devices',
                       'name': u'SEPACA016FDF235',
                       'device': u'SEPACA016FDF235',
                       'line': u'103',
                       'voicemail': u'103'}]

        sccpspeeddials = [{'exten': '1001',
                           'fknum': 1,
                           'label': 'user001',
                           'supervision': 0,
                           'user_id': 1229,
                           'device': 'SEPACA016FDF235'}]

        device_conf = _SccpDeviceConf(sccpspeeddials)
        device_conf._generate_devices(sccpdevice, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [SEPACA016FDF235](xivo_device_tpl)
            type = device
            line = 103
            voicemail = 103
            speeddial = 1229-1
        ''')

    def test_multiple_speedials_devices_section(self):
        sccpdevice = [{'category': u'devices',
                       'name': u'SEPACA016FDF235',
                       'device': u'SEPACA016FDF235',
                       'line': u'103',
                       'voicemail': u'103'}]

        sccpspeeddials = [
            {'exten': '1002',
             'fknum': 2,
             'label': 'user002',
             'supervision': 0,
             'user_id': 1229,
             'device': 'SEPACA016FDF235'},
            {'exten': '1001',
             'fknum': 1,
             'label': 'user001',
             'supervision': 0,
             'user_id': 1229,
             'device': 'SEPACA016FDF235'},
        ]

        device_conf = _SccpDeviceConf(sccpspeeddials)
        device_conf._generate_devices(sccpdevice, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [SEPACA016FDF235](xivo_device_tpl)
            type = device
            line = 103
            voicemail = 103
            speeddial = 1229-1
            speeddial = 1229-2
        ''')


class TestSccpLineConf(unittest.TestCase):

    def setUp(self):
        self._line_conf = _SccpLineConf(nova_compatibility=False)
        self._output = StringIO.StringIO()

    def test_template_directmedia_option(self):
        items = [
            {'option_name': 'directmedia', 'option_value': 'no'},
        ]

        self._line_conf._generate_template(items, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [xivo_line_tpl](!)
            directmedia = 0
        ''')

    def test_template_allow_option(self):
        items = [
            {'option_name': 'allow', 'option_value': 'ulaw'},
        ]

        self._line_conf._generate_template(items, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [xivo_line_tpl](!)
            disallow = all
            allow = ulaw
        ''')

    def test_template_empty_allow_option(self):
        items = [
            {'option_name': 'allow', 'option_value': ''},
        ]

        self._line_conf._generate_template(items, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [xivo_line_tpl](!)
        ''')

    def test_template_disallow_option_is_ignored(self):
        items = [
            {'option_name': 'disallow', 'option_value': 'foobar'},
        ]

        self._line_conf._generate_template(items, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [xivo_line_tpl](!)
        ''')

    def test_one_element_lines_section(self):
        uuid = str(uuid4())
        sccpline = [{
            'category': u'lines',
            'name': u'100',
            'cid_name': u'jimmy',
            'cid_num': u'100',
            'user_id': u'1',
            'uuid': uuid,
            'language': u'fr_FR',
            'number': u'100',
            'context': u'a_context',
        }]

        self._line_conf._generate_lines(sccpline, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [100](xivo_line_tpl)
            type = line
            cid_name = jimmy
            cid_num = 100
            setvar = XIVO_USERID=1
            setvar = XIVO_USERUUID={uuid}
            setvar = PICKUPMARK=100%a_context
            setvar = TRANSFER_CONTEXT=a_context
            setvar = CHANNEL(hangup_handler_push)=hangup_handlers,userevent,1
            language = fr_FR
            context = a_context
        '''.format(uuid=uuid))

    def test_one_element_lines_section_no_language(self):
        uuid = str(uuid4())
        sccpline = [{
            'category': u'lines',
            'name': u'100',
            'cid_name': u'jimmy',
            'cid_num': u'100',
            'user_id': u'1',
            'uuid': uuid,
            'language': None,
            'number': u'100',
            'context': u'a_context',
        }]

        self._line_conf._generate_lines(sccpline, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [100](xivo_line_tpl)
            type = line
            cid_name = jimmy
            cid_num = 100
            setvar = XIVO_USERID=1
            setvar = XIVO_USERUUID={uuid}
            setvar = PICKUPMARK=100%a_context
            setvar = TRANSFER_CONTEXT=a_context
            setvar = CHANNEL(hangup_handler_push)=hangup_handlers,userevent,1
            context = a_context
        '''.format(uuid=uuid))

    def test_allow_no_disallow(self):
        uuid = str(uuid4())
        sccpline = [{
            'category': u'lines',
            'name': u'100',
            'cid_name': u'jimmy',
            'cid_num': u'100',
            'user_id': u'1',
            'language': None,
            'number': u'100',
            'context': u'a_context',
            'allow': u'g729,ulaw',
            'uuid': uuid,
        }]

        self._line_conf._generate_lines(sccpline, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [100](xivo_line_tpl)
            type = line
            cid_name = jimmy
            cid_num = 100
            setvar = XIVO_USERID=1
            setvar = XIVO_USERUUID={uuid}
            setvar = PICKUPMARK=100%a_context
            setvar = TRANSFER_CONTEXT=a_context
            setvar = CHANNEL(hangup_handler_push)=hangup_handlers,userevent,1
            context = a_context
            allow = g729,ulaw
        '''.format(uuid=uuid))

    def test_disallow_all_allow_order(self):
        uuid = str(uuid4())
        sccpline = [{
            'category': u'lines',
            'name': u'100',
            'cid_name': u'jimmy',
            'cid_num': u'100',
            'user_id': u'1',
            'uuid': uuid,
            'language': None,
            'number': u'100',
            'context': u'a_context',
            'allow': u'g729,ulaw',
            'disallow': u'all',
        }]

        self._line_conf._generate_lines(sccpline, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [100](xivo_line_tpl)
            type = line
            cid_name = jimmy
            cid_num = 100
            setvar = XIVO_USERID=1
            setvar = XIVO_USERUUID={uuid}
            setvar = PICKUPMARK=100%a_context
            setvar = TRANSFER_CONTEXT=a_context
            setvar = CHANNEL(hangup_handler_push)=hangup_handlers,userevent,1
            context = a_context
            disallow = all
            allow = g729,ulaw
        '''.format(uuid=uuid))

    def test_call_and_pickup_groups(self):
        uuid = str(uuid4())
        sccpline = [
            {'category': u'lines',
             'name': u'100',
             'cid_name': u'jimmy',
             'cid_num': u'100',
             'user_id': u'1',
             'uuid': uuid,
             'language': None,
             'number': u'100',
             'context': u'a_context',
             'callgroup': [1, 2, 3, 4],
             'pickupgroup': [3, 4]},
        ]

        self._line_conf._generate_lines(sccpline, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [100](xivo_line_tpl)
            type = line
            cid_name = jimmy
            cid_num = 100
            setvar = XIVO_USERID=1
            setvar = XIVO_USERUUID={uuid}
            setvar = PICKUPMARK=100%a_context
            setvar = TRANSFER_CONTEXT=a_context
            setvar = CHANNEL(hangup_handler_push)=hangup_handlers,userevent,1
            context = a_context
            namedcallgroup = 1,2,3,4
            namedpickupgroup = 3,4
        '''.format(uuid=uuid))

    def test_nova_compatibility(self):
        self._line_conf = _SccpLineConf(nova_compatibility=True)
        uuid = str(uuid4())
        sccpline = [{
            'category': u'lines',
            'name': u'100',
            'cid_name': u'jimmy',
            'cid_num': u'100',
            'user_id': u'1',
            'uuid': uuid,
            'language': u'fr_FR',
            'number': u'1234',
            'context': u'a_context',
        }]

        self._line_conf._generate_lines(sccpline, self._output)

        assert_config_equal(self._output.getvalue(), '''
            [100](xivo_line_tpl)
            type = line
            cid_name = jimmy
            cid_num = 100
            setvar = XIVO_USERID=1
            setvar = XIVO_USERUUID={uuid}
            setvar = PICKUPMARK=1234%a_context
            setvar = TRANSFER_CONTEXT=a_context
            setvar = CHANNEL(hangup_handler_push)=hangup_handlers,userevent,1
            language = fr_FR
            context = a_context
            accountcode = 1234
        '''.format(uuid=uuid))
