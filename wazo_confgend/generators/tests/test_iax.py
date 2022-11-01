# -*- coding: utf-8 -*-
# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later



import unittest

from mock import patch, Mock
from wazo_confgend.generators.iax import IaxConf
from wazo_confgend.generators.tests.util import assert_generates_config


class TestIaxConf(unittest.TestCase):
    @patch('xivo_dao.asterisk_conf_dao.find_iax_general_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_iax_calllimits_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_iax_trunk_settings', Mock(return_value=[]))
    def test_empty_sections(self):
        iax_conf = IaxConf()
        assert_generates_config(iax_conf, '''
            [general]
        ''')

    @patch('xivo_dao.asterisk_conf_dao.find_iax_general_settings')
    @patch('xivo_dao.asterisk_conf_dao.find_iax_calllimits_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_iax_trunk_settings', Mock(return_value=[]))
    def test_general_section(self, find_iax_general_settings):
        find_iax_general_settings.return_value = [
            {'filename': 'iax.conf', 'category': 'general', 'var_name': 'bindport', 'var_val': '4569'},
            {'filename': 'iax.conf', 'category': 'general', 'var_name': 'bindaddr', 'var_val': '0.0.0.0'},
            {'filename': 'iax.conf', 'category': 'general', 'var_name': 'iaxcompat', 'var_val': 'no'},
            {'filename': 'iax.conf', 'category': 'general', 'var_name': 'authdebug', 'var_val': 'yes'},
            {'filename': 'iax.conf', 'category': 'general', 'var_name': 'srvlookup', 'var_val': None},
            {'filename': 'iax.conf', 'category': 'general', 'var_name': 'shrinkcallerid', 'var_val': None},
            {'filename': 'iax.conf', 'category': 'general', 'var_name': 'language', 'var_val': 'fr_FR'},
            {'filename': 'iax.conf', 'category': 'general', 'var_name': 'register', 'var_val': 'user:secret@host'},
            {'filename': 'iax.conf', 'category': 'general', 'var_name': 'allow', 'var_val': 'gsm,ulaw,alaw'},
        ]

        iax_conf = IaxConf()
        assert_generates_config(iax_conf, '''
            [general]
            bindport = 4569
            bindaddr = 0.0.0.0
            iaxcompat = no
            authdebug = yes
            language = fr_FR
            register => user:secret@host
            disallow = all
            allow = gsm
            allow = ulaw
            allow = alaw
        ''')
        find_iax_general_settings.assert_called_once_with()

    @patch('xivo_dao.asterisk_conf_dao.find_iax_general_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_iax_calllimits_settings')
    @patch('xivo_dao.asterisk_conf_dao.find_iax_trunk_settings', Mock(return_value=[]))
    def test_call_limits_section(self, find_iax_calllimits_settings):
        find_iax_calllimits_settings.return_value = [
            {'id': 1, 'destination': '192.168.2.1', 'netmask': '255.255.255.0', 'calllimits': 10},
            {'id': 1, 'destination': '10.0.0.1', 'netmask': '255.255.255.255', 'calllimits': 100},
        ]

        iax_conf = IaxConf()
        assert_generates_config(iax_conf, '''
            [general]
            [callnumberlimits]
            192.168.2.1/255.255.255.0 = 10
            10.0.0.1/255.255.255.255 = 100
        ''')
        find_iax_calllimits_settings.assert_called_once_with()

    @patch('xivo_dao.asterisk_conf_dao.find_iax_general_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_iax_calllimits_settings', Mock(return_value=[]))
    @patch('xivo_dao.asterisk_conf_dao.find_iax_trunk_settings')
    def test_trunk_section(self, find_iax_trunk_settings):
        trunk = Mock()
        trunk.name = 'wazo_devel_51'
        trunk.all_options.return_value = [
            ['type', 'friend'],
            ['username', 'wazo_devel_51'],
            ['secret', 'wazo_devel_51'],
            ['dbsecret', ''],
            ['context', 'default'],
            ['language', 'fr_FR'],
            ['accountcode', None],
            ['amaflags', None],
            ['mailbox', None],
            ['callerid', None],
            ['fullname', None],
            ['cid_number', None],
            ['trunk', 0],
            ['auth', 'plaintext,md5'],
            ['encryption', None],
            ['forceencryption', None],
            ['maxauthreq', None],
            ['inkeys', None],
            ['outkey', None],
            ['adsi', None],
            ['transfer', None],
            ['codecpriority', None],
            ['jitterbuffer', None],
            ['forcejitterbuffer', None],
            ['sendani', 0],
            ['qualify', 'no'],
            ['qualifysmoothing', 0],
            ['qualifyfreqok', 60000],
            ['qualifyfreqnotok', 10000],
            ['timezone', None],
            ['disallow', None],
            ['allow', None],
            ['mohinterpret', None],
            ['mohsuggest', None],
            ['deny', None],
            ['permit', None],
            ['defaultip', None],
            ['sourceaddress', None],
            ['setvar', ''],
            ['host', '192.168.32.253'],
            ['port', 4569],
            ['mask', None],
            ['regexten', None],
            ['peercontext', None],
            ['immediate', None],
            ['parkinglot', None],
            ['category', 'trunk'],
            ['commented', 0],
            ['requirecalltoken', 'auto'],
        ]
        find_iax_trunk_settings.return_value = [trunk]

        iax_conf = IaxConf()
        assert_generates_config(iax_conf, '''
            [general]
            [wazo_devel_51]
            type = friend
            username = wazo_devel_51
            secret = wazo_devel_51
            context = default
            language = fr_FR
            trunk = 0
            auth = plaintext,md5
            sendani = 0
            qualify = no
            qualifysmoothing = 0
            qualifyfreqok = 60000
            qualifyfreqnotok = 10000
            host = 192.168.32.253
            port = 4569
            category = trunk
            commented = 0
            requirecalltoken = auto
        ''')
        find_iax_trunk_settings.assert_called_once_with()
