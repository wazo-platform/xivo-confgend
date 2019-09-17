# -*- coding: utf-8 -*-
# Copyright 2011-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import sys

from mock import Mock

from wazo_confgend.asterisk import AsteriskFrontend


class Test(unittest.TestCase):

    def setUp(self):
        self._config = {
            'templates': {'contextsconf': None},
        }
        self.tpl_helper = Mock()
        self.asteriskFrontEnd = AsteriskFrontend(self._config, self.tpl_helper)

    def test_encoding(self):
        charset = ("ascii", "US-ASCII",)
        self.assertTrue(sys.getdefaultencoding() in charset, "Test should be run in ascii, in eclipse change run configuration common tab")

    def test_gen_iax_trunk(self):
        trunk = Mock()
        trunk.name = u'wazo_devel_51'
        trunk.all_options.return_value = [
            ['type', u'friend'],
            ['username', u'wazo_devel_51'],
            ['secret', u'wazo_devel_51'],
            ['dbsecret', u''],
            ['context', u'default'],
            ['language', u'fr_FR'],
            ['accountcode', None],
            ['amaflags', None],
            ['mailbox', None],
            ['callerid', None],
            ['fullname', None],
            ['cid_number', None],
            ['trunk', 0],
            ['auth', u'plaintext,md5'],
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
            ['qualify', u'no'],
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
            ['setvar', u''],
            ['host', u'192.168.32.253'],
            ['port', 4569],
            ['mask', None],
            ['regexten', None],
            ['peercontext', None],
            ['immediate', None],
            ['parkinglot', None],
            ['category', u'trunk'],
            ['commented', 0],
            ['requirecalltoken', u'auto'],
        ]

        result = self.asteriskFrontEnd._gen_iax_trunk(trunk)

        self.assertTrue(u'[wazo_devel_51]' in result)
        self.assertTrue(u'qualifysmoothing =  0' in result)
        self.assertTrue(u'secret =  wazo_devel_51' in result)
        self.assertTrue(u'type =  friend' in result)
        self.assertTrue(u'username =  wazo_devel_51' in result)
        self.assertTrue(u'auth =  plaintext,md5' in result)
        self.assertTrue(u'qualifyfreqnotok =  10000' in result)
        self.assertTrue(u'requirecalltoken =  auto' in result)
        self.assertTrue(u'port =  4569' in result)
        self.assertTrue(u'context =  default' in result)
        self.assertTrue(u'sendani =  0' in result)
        self.assertTrue(u'qualify =  no' in result)
        self.assertTrue(u'trunk =  0' in result)
        self.assertTrue(u'language =  fr_FR' in result)
        self.assertTrue(u'host =  192.168.32.253' in result)
        self.assertTrue(u'qualifyfreqok =  60000' in result)

    def test_gen_iax_conf_general(self):
        staticiax = [
            {'filename': u'iax.conf', 'category': u'general', 'var_name': u'bindport', 'var_val': u'4569'},
            {'filename': u'iax.conf', 'category': u'general', 'var_name': u'bindaddr', 'var_val': u'0.0.0.0'},
            {'filename': u'iax.conf', 'category': u'general', 'var_name': u'iaxcompat', 'var_val': u'no'},
            {'filename': u'iax.conf', 'category': u'general', 'var_name': u'authdebug', 'var_val': u'yes'},
            {'filename': u'iax.conf', 'category': u'general', 'var_name': u'srvlookup', 'var_val': None},
            {'filename': u'iax.conf', 'category': u'general', 'var_name': u'shrinkcallerid', 'var_val': None},
            {'filename': u'iax.conf', 'category': u'general', 'var_name': u'language', 'var_val': u'fr_FR'},
        ]

        result = self.asteriskFrontEnd._gen_iax_general(staticiax)

        self.assertTrue(u'[general]' in result)
        self.assertTrue(u'bindport = 4569' in result)
        self.assertTrue(u'bindaddr = 0.0.0.0' in result)
        self.assertTrue(u'iaxcompat = no' in result)
        self.assertTrue(u'authdebug = yes' in result)
        self.assertTrue(u'language = fr_FR' in result)
