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

import unittest
from mock import Mock
from hamcrest import assert_that, equal_to

from xivo_dao.alchemy.usersip import UserSIP as SIP

from xivo_confgen.generators.sip_trunk import SipTrunkGenerator
from xivo_confgen.generators.tests.util import assert_section_equal


class TestSipTrunkGenerator(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.dao.find_all_by.return_value = []
        self.generator = SipTrunkGenerator(self.dao)

    def generate_output(self):
        return '\n'.join(self.generator.generate())

    def test_given_no_sip_trunks_then_nothing_is_generated(self):
        output = self.generate_output()
        assert_that(output, equal_to(''))

    def test_trunk_generator_calls_dao_with_right_arguments(self):
        self.generate_output()
        self.dao.find_all_by.assert_called_once_with(commented=0, category='trunk')

    def test_given_one_trunk_with_minimal_parameters_then_one_section_is_generated(self):
        trunk = SIP(amaflags='default',
                    call_limit=10,
                    commented=0,
                    host=u'dynamic',
                    id=64,
                    name=u'trunksip',
                    protocol='sip',
                    regseconds=0,
                    subscribemwi=0,
                    type=u'peer',
                    _options=[])

        self.dao.find_all_by.return_value = [trunk]

        output = self.generate_output()
        assert_section_equal(output, '''
            [trunksip]
            amaflags = default
            regseconds = 0
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no
        ''')

    def test_given_allow_is_set_then_disallow_is_set_to_all(self):
        trunk = SIP(amaflags='default',
                    call_limit=10,
                    commented=0,
                    host=u'dynamic',
                    id=64,
                    name=u'trunksip',
                    protocol='sip',
                    regseconds=0,
                    subscribemwi=0,
                    type=u'peer',
                    allow='gsm',
                    _options=[])

        self.dao.find_all_by.return_value = [trunk]

        output = self.generate_output()
        assert_section_equal(output, '''
            [trunksip]
            amaflags = default
            regseconds = 0
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no
            disallow = all
            allow = gsm
        ''')

    def test_given_two_trunks_then_two_sections_generated(self):
        trunk1 = SIP(amaflags='default',
                     call_limit=10,
                     commented=0,
                     host=u'dynamic',
                     id=64,
                     name=u'trunksip1',
                     protocol='sip',
                     regseconds=0,
                     subscribemwi=0,
                     type=u'peer',
                     _options=[])

        trunk2 = SIP(amaflags='default',
                     call_limit=10,
                     commented=0,
                     host=u'dynamic',
                     id=65,
                     name=u'trunksip2',
                     protocol='sip',
                     regseconds=0,
                     subscribemwi=0,
                     type=u'peer',
                     _options=[])

        self.dao.find_all_by.return_value = [trunk1, trunk2]

        output = self.generate_output()
        assert_section_equal(output, '''
            [trunksip1]
            amaflags = default
            regseconds = 0
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no

            [trunksip2]
            amaflags = default
            regseconds = 0
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no
        ''')

    def test_given_trunk_with_all_options_then_all_options_in_section(self):
        trunk = SIP(id=1,
                    name='trunksip',
                    commented=0,
                    buggymwi=1,
                    category='trunk',
                    amaflags='default',
                    sendrpid='yes',
                    videosupport='yes',
                    maxcallbitrate=1024,
                    registertrying=1,
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
                    setvar='setvar',
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
                    _options=[])

        self.dao.find_all_by.return_value = [trunk]

        output = self.generate_output()
        assert_section_equal(output, '''
            [trunksip]
            buggymwi = 1
            amaflags = default
            sendrpid = yes
            videosupport = yes
            maxcallbitrate = 1024
            registertrying = 1
            session-minse = 10
            maxforwards = 1
            rtpholdtimeout = 15
            session-expires = 60
            ignoresdpversion = 1
            textsupport = 1
            unsolicited_mailbox = 1000@default
            fromuser = field-user
            useclientcode = 1
            call-limit = 1
            progressinband = yes
            transport = udp
            directmedia = update
            promiscredir = 1
            allowoverlap = 1
            dtmfmode = info
            language = fr_FR
            usereqphone = 1
            qualify = 500
            trustrpid = 1
            timert1 = 1
            session-refresher = uas
            allowsubscribe = 1
            session-timers = originate
            busylevel = 1
            callcounter = 0
            callerid = "cûstomcallerid" <1234>
            encryption = 1
            use_q850_reason = 1
            disallowed_methods = disallowsip
            rfc2833compensate = 1
            g726nonstandard = 1
            contactdeny = 127.0.0.1
            snom_aoc_enabled = 1
            t38pt_udptl = 1
            subscribemwi = no
            autoframing = 1
            t38pt_usertpsource = 1
            fromdomain = field-domain
            allowtransfer = 1
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
            setvar = setvar
            accountcode = accountcode
            md5secret = abcdefg
            mohinterpret = mohinterpret
            vmexten = 1000
            callingpres = 1
            parkinglot = 700
            fullcontact = fullcontact
            defaultip = 127.0.0.1
            qualifyfreq = 5000
            regexten = regexten
            regseconds = 60
            regserver = 127.0.0.1
            ipaddr = 127.0.0.1
            lastms = 500
            cid_number = 0123456789
            callbackextension = 0123456789
            port = 10000
            outboundproxy = 127.0.0.1
            remotesecret = remotesecret
        ''')

    def test_given_additional_options_then_generated_at_the_end_of_section(self):
        trunk = SIP(amaflags='default',
                    call_limit=10,
                    commented=0,
                    host=u'dynamic',
                    id=64,
                    name=u'trunksip',
                    protocol='sip',
                    regseconds=0,
                    subscribemwi=0,
                    type=u'peer',
                    _options=[
                        ['foo', 'bar'],
                        ['foo', 'baz'],
                        ['spam', 'eggs'],
                    ])

        self.dao.find_all_by.return_value = [trunk]

        output = self.generate_output()
        assert_section_equal(output, '''
            [trunksip]
            amaflags = default
            regseconds = 0
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no
            foo = bar
            foo = baz
            spam = eggs
        ''')
