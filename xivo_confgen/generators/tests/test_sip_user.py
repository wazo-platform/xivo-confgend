# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import unicode_literals
from collections import namedtuple

import unittest

from mock import Mock
from hamcrest import assert_that
from hamcrest import contains
from xivo_dao.alchemy.usersip import UserSIP as SIP

from xivo_confgen.generators.sip_user import SipUserGenerator
from xivo_confgen.generators.tests.util import assert_lines_contain

Row = namedtuple('Row', ['UserSIP', 'protocol', 'context', 'number', 'mohsuggest', 'user_id', 'uuid', 'mailbox',
                         'namedpickupgroup', 'namedcallgroup'])


class TestSipUserGenerator(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.dao.find_sip_user_settings.return_value = []
        self.generator = SipUserGenerator(self.dao)
        self.ccss_options = {
            'cc_agent_policy': 'generic',
            'cc_monitor_policy': 'generic',
            'cc_offer_timer': 30,
            'cc_recall_timer': 20,
            'ccbs_available_timer': 900,
            'ccnr_available_timer': 900,
        }

    def generate_output(self):
        lines = list(self.generator.generate(self.ccss_options))
        return lines

    def prepare_response(self, sip, **params):
        params.setdefault('user_id', None)
        params.setdefault('protocol', None)
        params.setdefault('context', None)
        params.setdefault('number', None)
        params.setdefault('mohsuggest', None)
        params.setdefault('uuid', None)
        params.setdefault('mailbox', None)
        params.setdefault('namedpickupgroup', None)
        params.setdefault('namedcallgroup', None)
        row = Row(UserSIP=sip, **params)
        self.dao.find_sip_user_settings.return_value = [row]

    def test_given_no_sip_users_then_nothing_is_generated(self):
        lines = self.generate_output()
        assert_that(lines, contains())

    def test_given_sip_account_has_minimal_parameters_then_one_section_is_generated(self):
        self.prepare_response(sip=SIP(amaflags='default',
                                      secret='secret',
                                      call_limit=10,
                                      commented=0,
                                      host='dynamic',
                                      id=64,
                                      name='user1',
                                      protocol='sip',
                                      regseconds=0,
                                      subscribemwi=0,
                                      type='friend',
                                      category='user',
                                      _options=[]))

        lines = self.generate_output()
        assert_lines_contain(
            lines,
            [
                '[user1]',
                'secret = secret',
                'amaflags = default',
                'call-limit = 10',
                'host = dynamic',
                'type = friend',
                'subscribemwi = no',
            ]
        )

    def test_given_sip_account_has_all_native_parameters_then_complete_section_is_generated(self):
        self.prepare_response(SIP(id=1,
                                  name='user1',
                                  username='username',
                                  secret='secret',
                                  commented=0,
                                  buggymwi=1,
                                  category='user',
                                  amaflags='default',
                                  sendrpid='yes',
                                  videosupport='yes',
                                  maxcallbitrate=1024,
                                  session_minse=10,
                                  maxforwards=1,
                                  rtpholdtimeout=15,
                                  session_expires=60,
                                  ignoresdpversion=1,
                                  textsupport=1,
                                  unsolicited_mailbox='1000@default',
                                  fromuser='field-user',
                                  useclientcode=1,
                                  call_limit=1,
                                  progressinband='yes',
                                  transport='udp',
                                  directmedia='update',
                                  promiscredir=1,
                                  allowoverlap=1,
                                  dtmfmode='info',
                                  language='fr_FR',
                                  usereqphone=1,
                                  qualify='500',
                                  trustrpid=1,
                                  timert1=1,
                                  session_refresher='uas',
                                  allowsubscribe=1,
                                  session_timers='originate',
                                  busylevel=1,
                                  callcounter=0,
                                  callerid='"cûstomcallerid" <1234>',
                                  encryption=1,
                                  use_q850_reason=1,
                                  disallowed_methods='disallowsip',
                                  rfc2833compensate=1,
                                  g726nonstandard=1,
                                  contactdeny='127.0.0.1',
                                  snom_aoc_enabled=1,
                                  t38pt_udptl=1,
                                  subscribemwi=0,
                                  autoframing=1,
                                  t38pt_usertpsource=1,
                                  fromdomain='field-domain',
                                  allowtransfer=1,
                                  nat='force_rport,comedia',
                                  contactpermit='127.0.0.1',
                                  rtpkeepalive=15,
                                  insecure='port',
                                  permit='127.0.0.1',
                                  deny='127.0.0.1',
                                  timerb=1,
                                  rtptimeout=15,
                                  disallow='all',
                                  allow='g723,gsm',
                                  accountcode='accountcode',
                                  md5secret='abcdefg',
                                  mohinterpret='mohinterpret',
                                  vmexten='1000',
                                  callingpres=1,
                                  parkinglot=700,
                                  fullcontact='fullcontact',
                                  defaultip='127.0.0.1',
                                  qualifyfreq=5000,
                                  protocol='sip',
                                  regexten='regexten',
                                  regseconds=60,
                                  regserver='127.0.0.1',
                                  ipaddr='127.0.0.1',
                                  lastms='500',
                                  cid_number='0123456789',
                                  callbackextension='0123456789',
                                  port=10000,
                                  outboundproxy='127.0.0.1',
                                  remotesecret='remotesecret',
                                  _options=[]))

        lines = self.generate_output()
        assert_lines_contain(
            lines,
            [
                '[user1]',
                'cc_agent_policy = generic',
                'cc_monitor_policy = generic',
                'cc_offer_timer = 30',
                'cc_recall_timer = 20',
                'ccbs_available_timer = 900',
                'ccnr_available_timer = 900',
                'buggymwi = yes',
                'secret = secret',
                'username = username',
                'amaflags = default',
                'sendrpid = yes',
                'videosupport = yes',
                'maxcallbitrate = 1024',
                'session-minse = 10',
                'maxforwards = 1',
                'rtpholdtimeout = 15',
                'session-expires = 60',
                'ignoresdpversion = yes',
                'textsupport = yes',
                'unsolicited_mailbox = 1000@default',
                'fromuser = field-user',
                'useclientcode = yes',
                'call-limit = 1',
                'progressinband = yes',
                'transport = udp',
                'directmedia = update',
                'promiscredir = yes',
                'allowoverlap = yes',
                'dtmfmode = info',
                'language = fr_FR',
                'usereqphone = yes',
                'qualify = 500',
                'trustrpid = yes',
                'timert1 = 1',
                'session-refresher = uas',
                'allowsubscribe = yes',
                'session-timers = originate',
                'busylevel = 1',
                'callcounter = no',
                'callerid = "cûstomcallerid" <1234>',
                'encryption = yes',
                'use_q850_reason = yes',
                'disallowed_methods = disallowsip',
                'rfc2833compensate = yes',
                'g726nonstandard = yes',
                'contactdeny = 127.0.0.1',
                'snom_aoc_enabled = yes',
                't38pt_udptl = yes',
                'subscribemwi = no',
                'autoframing = yes',
                't38pt_usertpsource = yes',
                'fromdomain = field-domain',
                'allowtransfer = yes',
                'nat = force_rport,comedia',
                'contactpermit = 127.0.0.1',
                'rtpkeepalive = 15',
                'insecure = port',
                'permit = 127.0.0.1',
                'deny = 127.0.0.1',
                'timerb = 1',
                'rtptimeout = 15',
                'allow = g723,gsm',
                'accountcode = accountcode',
                'md5secret = abcdefg',
                'mohinterpret = mohinterpret',
                'vmexten = 1000',
                'callingpres = 1',
                'parkinglot = 700',
                'defaultip = 127.0.0.1',
                'qualifyfreq = 5000',
                'regexten = regexten',
                'regserver = 127.0.0.1',
                'cid_number = 0123456789',
                'callbackextension = 0123456789',
                'port = 10000',
                'outboundproxy = 127.0.0.1',
                'remotesecret = remotesecret',
                'description = "cûstomcallerid" <1234>',
                'setvar = XIVO_ORIGINAL_CALLER_ID="cûstomcallerid" <1234>',
            ]
        )

    def test_given_sip_has_additional_options_then_options_generated_at_the_end_of_secition(self):
        self.prepare_response(SIP(secret='secret',
                                  host=u'dynamic',
                                  name=u'user',
                                  type=u'friend',
                                  _options=[
                                      ['foo', 'bar'],
                                      ['foo', 'baz'],
                                      ['spam', 'eggs'],
                                  ]))

        lines = self.generate_output()
        assert_lines_contain(
            lines,
            [
                '[user]',
                'secret = secret',
                'host = dynamic',
                'type = friend',
                'foo = bar',
                'foo = baz',
                'spam = eggs',
            ]
        )

    def test_given_sip_account_associated_to_resources_then_resources_generated_in_section(self):
        self.prepare_response(sip=SIP(name='user', _options=[]),
                              number='1000',
                              context='default',
                              protocol='sip',
                              mohsuggest='musiconhold',
                              user_id=42,
                              uuid='user-uuid',
                              mailbox='1001@default',
                              namedpickupgroup='1,2',
                              namedcallgroup='3,4')

        lines = self.generate_output()
        assert_lines_contain(
            lines,
            [
                '[user]',
                'mohsuggest = musiconhold',
                'setvar = PICKUPMARK=1000%default',
                'setvar = TRANSFER_CONTEXT=default',
                'setvar = XIVO_USERID=42',
                'setvar = XIVO_USERUUID=user-uuid',
                'namedpickupgroup = 1,2',
                'namedcallgroup = 3,4',
                'mailbox = 1001@default',
            ]
        )

    def test_given_ccss_options_when_generating_then_ccss_options_in_section(self):
        self.prepare_response(sip=SIP(name='user', _options=[]))
        lines = self.generate_output()
        assert_lines_contain(
            lines,
            [
                '[user]',
                'cc_agent_policy = generic',
                'cc_monitor_policy = generic',
                'cc_offer_timer = 30',
                'cc_recall_timer = 20',
                'ccbs_available_timer = 900',
                'ccnr_available_timer = 900',
            ]
        )

    def test_given_sip_allow_codecs_is_set_then_allow_parameters_generated_in_section(self):
        self.prepare_response(sip=SIP(name='user',
                                      _options=[],
                                      allow='gsm,alaw',
                                      disallow='g729'))

        lines = self.generate_output()
        assert_lines_contain(
            lines,
            [
                '[user]',
                'disallow = all',
                'allow = gsm,alaw',
            ]
        )

    def test_nova_compatibility_adds_accountcode(self):
        self.generator = SipUserGenerator(self.dao, nova_compatibility=True)
        self.prepare_response(sip=SIP(name='user', _options=[]),
                              number='1000',
                              context='default')

        lines = self.generate_output()
        assert_lines_contain(
            lines,
            [
                '[user]',
                'accountcode = 1000',
            ]
        )
