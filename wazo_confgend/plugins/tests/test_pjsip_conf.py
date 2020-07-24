# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from collections import namedtuple

from mock import Mock, patch

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    none,
)
from StringIO import StringIO
from xivo_dao.alchemy.pjsip_transport import PJSIPTransport
from wazo_confgend.generators.tests.util import assert_config_equal

from ..pjsip_registration import Registration
from ..pjsip_conf import (
    AsteriskConfFileGenerator,
    Section,
    SipDBExtractor,
    PJSIPConfGenerator,
)

SearchResult = namedtuple('SearchResult', ['total', 'items'])


class TestPJSIPConfGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = PJSIPConfGenerator(dependencies=None)

    def test_generate_transports(self):
        output = StringIO()
        with patch('wazo_confgend.plugins.pjsip_conf.transport_dao') as dao:
            dao.search.return_value = SearchResult(2, [
                PJSIPTransport(
                    name='transport-udp',
                    options=[
                        ['protocol', 'udp'],
                        ['bind', '0.0.0.0:5060'],
                    ]
                ),
                PJSIPTransport(
                    name='transport-wss',
                    options=[
                        ['protocol', 'wss'],
                        ['bind', '0.0.0.0:5060'],
                    ]
                ),
            ])

            self.generator.generate_transports(output)
            assert_config_equal(
                output.getvalue(),
                '''\
                [transport-udp]
                type = transport
                protocol = udp
                bind = 0.0.0.0:5060

                [transport-wss]
                type = transport
                protocol = wss
                bind = 0.0.0.0:5060
                '''
            )

    def test_generate_users(self):
        output = StringIO()
        name_1 = 'abcdef'
        label_1 = 'my-sip-line'
        name_2 = 'defbca'
        label_2 = 'another-sip-line'
        with patch('wazo_confgend.plugins.pjsip_conf.asterisk_conf_dao') as dao:
            dao.find_sip_user_settings.return_value = [
                {
                    'name': name_1,
                    'label': label_1,
                    'aor_section_options': [
                        ['type', 'aor'],
                        ['qualify_frequency', '60'],
                    ],
                    'auth_section_options': [
                        ['type', 'auth'],
                        ['username', 'iddqd'],
                    ],
                    'endpoint_section_options': [
                        ['type', 'endpoint'],
                        ['aors', name_1],
                        ['auth', name_1],
                        ['allow', '!all,ulaw'],
                    ],
                },
                {
                    'name': name_2,
                    'label': label_2,
                    'aor_section_options': [
                        ['type', 'aor'],
                        ['qualify_frequency', '42'],
                    ],
                    'auth_section_options': [
                        ['type', 'auth'],
                        ['username', 'idbehold'],
                    ],
                    'endpoint_section_options': [
                        ['type', 'endpoint'],
                        ['aors', name_2],
                        ['auth', name_2],
                        ['allow', '!all,ulaw,g729'],
                    ],
                },
            ]

            self.generator.generate_lines(output)
            result = output.getvalue()
            assert_config_equal(
                result,
                '''\
                ; {label_1}
                [{name_1}]
                type = endpoint
                aors = {name_1}
                auth = {name_1}
                allow = !all,ulaw

                [{name_1}]
                type = aor
                qualify_frequency = 60

                [{name_1}]
                type = auth
                username = iddqd

                ; {label_2}
                [{name_2}]
                type = endpoint
                aors = {name_2}
                auth = {name_2}
                allow = !all,ulaw,g729

                [{name_2}]
                type = aor
                qualify_frequency = 42

                [{name_2}]
                type = auth
                username = idbehold
                '''.format(
                    label_1=label_1,
                    label_2=label_2,
                    name_1=name_1,
                    name_2=name_2,
                )
            )

    def test_generate_trunks(self):
        output = StringIO()
        name_1 = 'abcdef'
        label_1 = 'my-sip-trunk'
        with patch('wazo_confgend.plugins.pjsip_conf.asterisk_conf_dao') as dao:
            dao.find_sip_trunk_settings.return_value = [
                {
                    'name': name_1,
                    'label': label_1,
                    'aor_section_options': [
                        ['type', 'aor'],
                        ['qualify_frequency', '60'],
                    ],
                    'auth_section_options': [
                        ['type', 'auth'],
                        ['username', 'iddqd'],
                    ],
                    'endpoint_section_options': [
                        ['type', 'endpoint'],
                        ['aors', name_1],
                        ['auth', name_1],
                        ['allow', '!all,ulaw'],
                        ['outbound_auth', 'outbound_auth_{}'.format(name_1)],
                    ],
                    'identify_section_options': [
                        ['type', 'identify'],
                        ['match', '54.172.60.0'],
                        ['match', '54.172.60.1'],
                        ['endpoint', name_1],
                    ],
                    'registration_section_options': [
                        ['type', 'registration'],
                        ['expiration', '120'],
                        ['outbound_auth', 'auth_reg_dev_370@wazo-dev-gateway.lan.wazo.io'],
                    ],
                    'registration_outbound_auth_section_options': [
                        ['type', 'auth'],
                        ['username', 'reg_username'],
                        ['password', 'secret'],
                    ],
                    'outbound_auth_section_options': [
                        ['type', 'auth'],
                        ['username', 'outbound_auth_username'],
                        ['password', 'secret'],
                    ],
                },
            ]

            self.generator.generate_trunks(output)
            result = output.getvalue()
            assert_config_equal(
                result,
                '''\
                ; {label_1}
                [{name_1}]
                type = endpoint
                aors = {name_1}
                auth = {name_1}
                allow = !all,ulaw
                outbound_auth = outbound_auth_{name_1}

                [{name_1}]
                type = aor
                qualify_frequency = 60

                [{name_1}]
                type = auth
                username = iddqd

                [{name_1}]
                type = identify
                match = 54.172.60.0
                match = 54.172.60.1
                endpoint = {name_1}

                [outbound_auth_{name_1}]
                type = auth
                username = outbound_auth_username
                password = secret

                [auth_reg_dev_370@wazo-dev-gateway.lan.wazo.io]
                type = auth
                username = reg_username
                password = secret

                [{name_1}]
                type = registration
                expiration = 120
                outbound_auth = auth_reg_dev_370@wazo-dev-gateway.lan.wazo.io
                '''.format(label_1=label_1, name_1=name_1)
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
        assert_that(result, none())

        result = SipDBExtractor._convert_dtmfmode({'dtmfmode': 'rfc2833'})
        assert_that(result, contains('dtmf_mode', 'rfc4733'))

        result = SipDBExtractor._convert_dtmfmode({'dtmfmode': 'inband'})
        assert_that(result, contains('dtmf_mode', 'inband'))

        result = SipDBExtractor._convert_dtmfmode({'dtmfmode': 'info'})
        assert_that(result, contains('dtmf_mode', 'info'))

    def test_convert_insecure(self):
        result = SipDBExtractor._convert_insecure({'name': 'name'})
        assert_that(result, contains('auth', 'name'))

        result = SipDBExtractor._convert_insecure({'name': 'name', 'insecure': 'invite'})
        assert_that(result, none())

        result = SipDBExtractor._convert_insecure({'name': 'name', 'insecure': 'port,invite'})
        assert_that(result, none())

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

    def test_convert_register(self):
        transport_udp = Mock()
        transport_udp.name = 'transport_udp'
        configured_transports = Mock(items=[transport_udp])

        register_url = 'transport-udp://dev_370:dev_370:dev_370@wazo-dev-gateway.lan.wazo.io'
        register = Registration(register_url, configured_transports)

        result = list(SipDBExtractor._convert_register(register_url, configured_transports))
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
        sip = Mock(host='dynamic', _options=[['max_contacts', 3]])
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('max_contacts', 3)
            ),
        )

        sip = Mock(host='dynamic', _options=[])
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('max_contacts', 1),
                ('remove_existing', 'yes')
            )
        )

        sip = Mock(host='dynamic', _options=[['webrtc', 'yes']])
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('max_contacts', 10),
            )
        )

        sip = Mock(host='dynamic', _options=[['webrtc', 'yes'], ['max_contacts', 42]])
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('max_contacts', 42),
            )
        )

        sip = Mock(host='localhost', port=None, username=None, _options=[])
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('contact', 'sip:localhost:5060'),
            )
        )

        sip = Mock(host='localhost', port=6000, username=None, _options=[])
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('contact', 'sip:localhost:6000'),
            )
        )

        sip = Mock(host='localhost', port=None, username='abcdef', _options=[])
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('contact', 'sip:abcdef@localhost:5060'),
            )
        )

        sip = Mock(host='localhost', port=None, category='user', _options=[])
        sip.name = 'abcdef'
        result = list(SipDBExtractor._convert_host(sip))
        assert_that(
            result,
            contains_inanyorder(
                ('qualify_frequency', 0),
                ('contact', 'sip:abcdef@localhost:5060'),
            )
        )
