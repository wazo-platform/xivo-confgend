# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    none,
)

from ..pjsip_registration import Registration
from ..pjsip_conf import (
    AsteriskConfFileGenerator,
    Section,
    SipDBExtractor,
)


class TestConfFileGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = AsteriskConfFileGenerator()

    def test_generate(self):
        data = [
            Section('global', 'section', None, [('type', 'global'), ('user_agent', 'Wazo')]),
            Section('global', 'extends', None, [('debug', 'yes')]),
            Section('general-abc', 'template', None, [('disallow', 'all'), ('allow', 'ulaw')]),
            Section('webrtc-endpoint', 'template', ['a', 'b'], [('transport', 'transport-wss')]),
            Section('peer1', 'section', ['general-abc'], [('type', 'endpoint')]),
            Section('peer1', 'extends', ['webrtc-endpoint'], [('context', 'inside')]),
        ]

        result = self.generator.generate(data)

        expected = '''\
[global]
type = global
user_agent = Wazo

[global](+)
debug = yes

[general-abc](!)
disallow = all
allow = ulaw

[webrtc-endpoint](!,a,b)
transport = transport-wss

[peer1](general-abc)
type = endpoint

[peer1](+,webrtc-endpoint)
context = inside
'''

        assert_that(result, equal_to(expected))


class TestSipDBExtractor(unittest.TestCase):

    def test_add_option(self):
        fields = []

        SipDBExtractor._add_option(fields, None)
        assert_that(fields, empty())

        SipDBExtractor._add_option(fields, ('foo', 'bar'))
        assert_that(fields, contains(('foo', 'bar')))

    def test_convert_dtmfmode(self):
        result = SipDBExtractor._convert_dtmfmode({})
        assert_that(result, none())

        result = SipDBExtractor._convert_dtmfmode({'dtmfmode': 'foobar'})
        assert_that(result, contains('dtmf_mode', 'foobar'))

        result = SipDBExtractor._convert_dtmfmode({'dtmfmode': 'rfc2833'})
        assert_that(result, contains('dtmf_mode', 'rfc4733'))

    def test_convert_nat(self):
        result = SipDBExtractor._convert_nat({})
        assert_that(list(result), empty())

        result = SipDBExtractor._convert_nat({'nat': 'yes'})
        assert_that(
            list(result),
            contains(
                contains('rtp_symmetric', 'yes'),
                contains('rewrite_contact', 'yes'),
            )
        )

        result = SipDBExtractor._convert_nat({'nat': 'comedia'})
        assert_that(
            list(result),
            contains(
                contains('rtp_symmetric', 'yes'),
            )
        )

        result = SipDBExtractor._convert_nat({'nat': 'force_rport'})
        assert_that(
            list(result),
            contains(
                contains('force_rport', 'yes'),
                contains('rewrite_contact', 'yes'),
            )
        )

    def test_convert_session_timers(self):
        result = SipDBExtractor._convert_session_timers({})
        assert_that(result, none())

        result = SipDBExtractor._convert_session_timers({'session-timers': 'originate'})
        assert_that(result, contains('timers', 'always'))

        result = SipDBExtractor._convert_session_timers({'session-timers': 'accept'})
        assert_that(result, contains('timers', 'required'))

        result = SipDBExtractor._convert_session_timers({'session-timers': 'never'})
        assert_that(result, contains('timers', 'no'))

        result = SipDBExtractor._convert_session_timers({'session-timers': 'yes'})
        assert_that(result, contains('timers', 'yes'))

    def test_convert_directmedia(self):
        result = SipDBExtractor._convert_directmedia({'directmedia': 'yes'})
        assert_that(
            result,
            contains(
                contains('direct_media', 'yes'),
            )
        )

        result = SipDBExtractor._convert_directmedia({'directmedia': 'update'})
        assert_that(
            result,
            contains(
                contains('direct_media_method', 'update'),
            )
        )

        result = SipDBExtractor._convert_directmedia({'directmedia': 'outgoing'})
        assert_that(
            result,
            contains(
                contains('direct_media_glare_mitigation', 'outgoing'),
            )
        )

        result = SipDBExtractor._convert_directmedia({'directmedia': 'nonat'})
        assert_that(
            result,
            contains(
                contains('disable_directed_media_on_nat', 'yes'),
            )
        )

        result = SipDBExtractor._convert_directmedia({'directmedia': 'no'})
        assert_that(
            result,
            contains(
                contains('direct_media', 'no'),
            )
        )

        result = SipDBExtractor._convert_directmedia({'directmedia': 'yes,update,outgoing'})
        assert_that(
            result,
            contains(
                contains('direct_media', 'yes'),
                contains('direct_media_method', 'update'),
                contains('direct_media_glare_mitigation', 'outgoing'),
            )
        )

    def test_convert_sendrpid(self):
        result = SipDBExtractor._convert_sendrpid({})
        assert_that(result, none())

        result = SipDBExtractor._convert_sendrpid({'sendrpid': 'yes'})
        assert_that(result, contains('send_rpid', 'yes'))

        result = SipDBExtractor._convert_sendrpid({'sendrpid': 'rpid'})
        assert_that(result, contains('send_rpid', 'yes'))

        result = SipDBExtractor._convert_sendrpid({'sendrpid': 'pai'})
        assert_that(result, contains('send_pai', 'yes'))

    def test_convert_tcpbindaddr(self):
        result = SipDBExtractor._convert_tcpbindaddr({})
        assert_that(result, none())

        result = SipDBExtractor._convert_tcpbindaddr({'tcpbindaddr': '0.0.0.0:1234'})
        assert_that(result, contains('bind', '0.0.0.0'))

    def test_convert_encryption(self):
        result = SipDBExtractor._convert_encryption({})
        assert_that(result, none())

        result = SipDBExtractor._convert_encryption({'encryption': 'yes'})
        assert_that(result, contains('media_encryption', 'sdes'))

    def test_convert_progressinband(self):
        result = SipDBExtractor._convert_progressinband({})
        assert_that(result, none())

        result = SipDBExtractor._convert_progressinband({'progressinband': 'yes'})
        assert_that(result, contains('inband_progress', 'yes'))

        result = SipDBExtractor._convert_progressinband({'progressinband': 'no'})
        assert_that(result, contains('inband_progress', 'no'))

        result = SipDBExtractor._convert_progressinband({'progressinband': 'never'})
        assert_that(result, contains('inband_progress', 'no'))

    def test_convert_externtcpport(self):
        result = SipDBExtractor._convert_externtcpport({})
        assert_that(result, none())

        result = SipDBExtractor._convert_externtcpport({'externtcpport': ''})
        assert_that(result, none())

        result = SipDBExtractor._convert_externtcpport({'externtcpport': 1234})
        assert_that(result, contains('external_signaling_port', 1234))

    def test_convert_register(self):
        register_url = 'udp://dev_370:dev_370:dev_370@wazo-dev-gateway.lan.wazo.io'
        register = Registration(register_url)

        result = list(SipDBExtractor._convert_register(register_url))
        assert_that(
            result,
            contains_inanyorder(
                Section(
                    name=register.section,
                    type_='section',
                    templates=['wazo-general-registration'],
                    fields=register.registration_fields + [
                        ('type', 'registration'),
                        ('outbound_auth', register.auth_section),
                    ]
                ),
                Section(
                    name=register.auth_section,
                    type_='section',
                    templates=None,
                    fields=register.auth_fields + [
                        ('type', 'auth'),
                    ]
                ),
            )
        )

    def test_convert_host(self):
        sip = Mock(host='dynamic')
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('max_contacts', 1),
                ('remove_existing', 'yes')
            )
        )

        sip = Mock(host='localhost', port=None, username=None)
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('contact', 'sip:localhost:5060'),
            )
        )

        sip = Mock(host='localhost', port=6000, username=None)
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('contact', 'sip:localhost:6000'),
            )
        )

        sip = Mock(host='localhost', port=None, username='abcdef')
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('contact', 'sip:abcdef@localhost:5060'),
            )
        )
