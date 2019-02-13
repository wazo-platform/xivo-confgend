# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import unittest

from mock import Mock
from hamcrest import assert_that, contains_string, equal_to, empty
from jinja2.loaders import PackageLoader

from xivo_dao.alchemy.usersip import UserSIP as SIP

from xivo_confgen.generators.tests.util import assert_section_equal
from xivo_confgen.template import TemplateHelper

from ..sip_conf import _SipTrunkGenerator
from ..sip_conf import _TwilioConfigGenerator


class TestSipTrunkGenerator(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.dao.find_sip_trunk_settings.return_value = []
        self.twilio_config_generator = Mock()
        self.twilio_config_generator.generate.return_value = ''
        self.generator = _SipTrunkGenerator(self.dao, self.twilio_config_generator)

    def generate_output(self):
        return '\n'.join(self.generator.generate())

    def test_given_no_sip_trunks_then_nothing_is_generated(self):
        output = self.generate_output()
        assert_that(output, equal_to(''))

    def test_trunk_generator_calls_dao_with_right_arguments(self):
        self.generate_output()
        self.dao.find_sip_trunk_settings.assert_called_once_with()

    def test_given_one_trunk_with_minimal_parameters_then_one_section_is_generated(self):
        endpoint = SIP(amaflags='default',
                       call_limit=10,
                       commented=0,
                       host=u'dynamic',
                       id=64,
                       name=u'trunksip',
                       protocol='sip',
                       subscribemwi=0,
                       type=u'peer',
                       _options=[])
        trunk = Mock(UserSIP=endpoint)

        self.dao.find_sip_trunk_settings.return_value = [trunk]

        output = self.generate_output()
        assert_section_equal(output, '''
            [trunksip]
            amaflags = default
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no
        ''')

    def test_given_allow_is_set_then_disallow_is_set_to_all(self):
        endpoint = SIP(amaflags='default',
                       call_limit=10,
                       commented=0,
                       host=u'dynamic',
                       id=64,
                       name=u'trunksip',
                       protocol='sip',
                       subscribemwi=0,
                       type=u'peer',
                       allow='gsm',
                       _options=[])
        trunk = Mock(UserSIP=endpoint)

        self.dao.find_sip_trunk_settings.return_value = [trunk]

        output = self.generate_output()
        assert_section_equal(output, '''
            [trunksip]
            amaflags = default
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no
            disallow = all
            allow = gsm
        ''')

    def test_given_two_trunks_then_two_sections_generated(self):
        endpoint1 = SIP(amaflags='default',
                        call_limit=10,
                        commented=0,
                        host=u'dynamic',
                        id=64,
                        name=u'trunksip1',
                        protocol='sip',
                        subscribemwi=0,
                        type=u'peer',
                        _options=[])
        trunk1 = Mock(UserSIP=endpoint1)

        endpoint2 = SIP(amaflags='default',
                        call_limit=10,
                        commented=0,
                        host=u'dynamic',
                        id=65,
                        name=u'trunksip2',
                        protocol='sip',
                        subscribemwi=0,
                        type=u'peer',
                        _options=[])
        trunk2 = Mock(UserSIP=endpoint2)

        self.dao.find_sip_trunk_settings.return_value = [trunk1, trunk2]

        output = self.generate_output()
        assert_section_equal(output, '''
            [trunksip1]
            amaflags = default
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no

            [trunksip2]
            amaflags = default
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no
        ''')

    def test_given_trunk_with_all_options_then_all_options_in_section(self):
        endpoint = SIP(id=1,
                       name='trunksip',
                       commented=0,
                       buggymwi=1,
                       category='trunk',
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
                       defaultip='127.0.0.1',
                       qualifyfreq=5000,
                       protocol='sip',
                       regexten='regexten',
                       cid_number='0123456789',
                       callbackextension='0123456789',
                       port=10000,
                       outboundproxy='127.0.0.1',
                       remotesecret='remotesecret',
                       _options=[])
        trunk = Mock(UserSIP=endpoint)

        self.dao.find_sip_trunk_settings.return_value = [trunk]

        output = self.generate_output()
        assert_section_equal(output, '''
            [trunksip]
            buggymwi = yes
            amaflags = default
            sendrpid = yes
            videosupport = yes
            maxcallbitrate = 1024
            session-minse = 10
            maxforwards = 1
            rtpholdtimeout = 15
            session-expires = 60
            ignoresdpversion = yes
            textsupport = yes
            unsolicited_mailbox = 1000@default
            fromuser = field-user
            useclientcode = yes
            call-limit = 1
            progressinband = yes
            transport = udp
            directmedia = update
            promiscredir = yes
            allowoverlap = yes
            dtmfmode = info
            language = fr_FR
            usereqphone = yes
            qualify = 500
            trustrpid = yes
            timert1 = 1
            session-refresher = uas
            allowsubscribe = yes
            session-timers = originate
            busylevel = 1
            callcounter = no
            callerid = "cûstomcallerid" <1234>
            encryption = yes
            use_q850_reason = yes
            disallowed_methods = disallowsip
            rfc2833compensate = yes
            g726nonstandard = yes
            contactdeny = 127.0.0.1
            snom_aoc_enabled = yes
            t38pt_udptl = yes
            subscribemwi = no
            autoframing = yes
            t38pt_usertpsource = yes
            fromdomain = field-domain
            allowtransfer = yes
            nat = force_rport,comedia
            contactpermit = 127.0.0.1
            rtpkeepalive = 15
            insecure = port
            permit = 127.0.0.1
            deny = 127.0.0.1
            timerb = 1
            rtptimeout = 15
            disallow = all
            allow = g723,gsm
            accountcode = accountcode
            md5secret = abcdefg
            mohinterpret = mohinterpret
            vmexten = 1000
            callingpres = 1
            parkinglot = 700
            defaultip = 127.0.0.1
            qualifyfreq = 5000
            regexten = regexten
            cid_number = 0123456789
            callbackextension = 0123456789
            port = 10000
            outboundproxy = 127.0.0.1
            remotesecret = remotesecret
        ''')

    def test_given_additional_options_then_generated_at_the_end_of_section(self):
        endpoint = SIP(amaflags='default',
                       call_limit=10,
                       commented=0,
                       host=u'dynamic',
                       id=64,
                       name=u'trunksip',
                       protocol='sip',
                       subscribemwi=0,
                       type=u'peer',
                       _options=[
                           ['foo', 'bar'],
                           ['foo', 'baz'],
                           ['spam', 'eggs'],
                       ])
        trunk = Mock(UserSIP=endpoint)

        self.dao.find_sip_trunk_settings.return_value = [trunk]

        output = self.generate_output()
        assert_section_equal(output, '''
            [trunksip]
            amaflags = default
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no
            foo = bar
            foo = baz
            spam = eggs
        ''')

    def test_twilio_config_generator_is_used(self):
        self.twilio_config_generator.generate.return_value = 'twilio config'
        self.dao.find_sip_trunk_settings.return_value = []

        output = self.generate_output()

        assert_that(output, contains_string('twilio config'))
        self.twilio_config_generator.generate.assert_called_once_with([])


class TestTwilioConfigGenerator(unittest.TestCase):

    def setUp(self):
        loader = PackageLoader('xivo_confgen.template')
        self.tpl_helper = TemplateHelper(loader)
        self.generator = _TwilioConfigGenerator(self.tpl_helper)

    def test_no_twilio_incoming_trunks(self):
        trunks = [Mock(twilio_incoming=False)]

        output = self.generator.generate(trunks)

        assert_that(output, empty())

    def test_template_renders_correctly(self):
        endpoint = SIP(
            commented=0,
            id=64,
            name=u'trunksip',
            protocol='sip',
            type=u'peer',
            _options=[]
        )
        trunks = [Mock(UserSIP=endpoint, twilio_incoming=True)]

        output = self.generator.generate(trunks)

        assert_that(output, contains_string('[twilio-gateway01](twilio-gateway-tpl)'))
