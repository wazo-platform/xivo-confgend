# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+
from __future__ import unicode_literals

from collections import namedtuple
from xivo_dao import asterisk_conf_dao

from .pjsip_registration import Registration

Section = namedtuple('Section', ['name', 'type_', 'templates', 'fields'])


class AsteriskConfFileGenerator(object):

    def generate(self, sections):
        lines = []

        for section in sections:
            if not section:
                continue
            name, type_, templates, fields = section
            fields = fields or []
            header = self._build_header(name, type_, templates)

            lines.append(header)
            for key, value in fields:
                lines.append('{} = {}'.format(key, value))
            lines.append('')

        return '\n'.join(lines)

    def _build_header(self, name, type_, templates):
        templates = templates or []
        in_parens = []

        if type_ == 'extends':
            in_parens.append('+')
        elif type_ == 'template':
            in_parens.append('!')

        for template in templates:
            in_parens.append(template)

        end = '({})'.format(','.join(in_parens)) if in_parens else ''
        return '[{}]{}'.format(name, end)


class SipDBExtractor(object):

    sip_general_to_global = [
        ('useragent', 'user_agent'),
        ('sipdebug', 'debug'),
        ('legacy_useroption_parsing', 'ignore_uri_user_options'),
    ]
    sip_general_to_system = [
        ('timert1', 'timer_t1'),
        ('timerb', 'timer_b'),
        ('compactheaders', 'compact_headers'),
    ]
    sip_general_to_transport = [
        ('media_address', 'external_media_address'),
    ]
    sip_general_to_register_tpl = [
        ('registertimeout', 'retry_interval'),
        ('registerattempts', 'max_retries'),
        ('outboundproxy', 'outbound_proxy'),
    ]
    sip_to_aor = [
        ('qualifyfreq', 'qualify_frequency'),
        ('maxexpiry', 'maximum_expiration'),
        ('minexpiry', 'minimum_expiration'),
        ('defaultexpiry', 'default_expiration'),
    ]
    sip_to_endpoint = [
        ('allowsubscribe', 'allow_subscribe'),
        ('allowtransfer', 'allow_transfer'),
        ('autoframing', 'use_ptime'),
        ('avpf', 'use_avpf'),
        ('busylevel', 'device_state_busy_at'),
        ('callerid', 'callerid'),
        ('callingpres', 'callerid_privacy'),
        ('cid_tag', 'callerid_tag'),
        ('cos_audio', 'cos_audio'),
        ('cos_video', 'cos_video'),
        ('dtlscafile', 'dtls_ca_file'),
        ('dtlscapath', 'dtls_ca_path'),
        ('dtlscertfile', 'dtls_cert_file'),
        ('dtlscipher', 'dtls_cipher'),
        ('dtlsprivatekey', 'dtls_private_key'),
        ('dtlsrekey', 'dtls_rekey'),
        ('dtlssetup', 'dtls_setup'),
        ('dtlsverify', 'dtls_verify'),
        ('fromdomain', 'from_domain'),
        ('fromdomain', 'from_domain'),
        ('fromuser', 'from_user'),
        ('icesupport', 'ice_support'),
        ('language', 'language'),
        ('max_audio_streams', 'max_audio_streams'),
        ('max_video_streams', 'max_video_streams'),
        ('mohsuggest', 'moh_suggest'),
        ('mwifrom', 'mwi_from_user'),
        ('outboundproxy', 'outbound_proxy'),
        ('rtcp_mux', 'rtcp_mux'),
        ('rtp_engine', 'rtp_engine'),
        ('rtptimeout', 'rtp_timeout'),
        ('sdpowner', 'sdp_owner'),
        ('sdpowner', 'sdp_owner'),
        ('sdpsession', 'sdp_session'),
        ('sdpsession', 'sdp_session'),
        ('send_diversion', 'send_diversion'),
        ('session-expires', 'timers_sess_expires'),
        ('session-minse', 'timers_min_se'),
        ('subminexpiry', 'sub_min_expiry'),
        ('tonezone', 'tone_zone'),
        ('tos_audio', 'tos_audio'),
        ('tos_video', 'tos_video'),
        ('trustpid', 'trust_id_inbound'),
        ('webrtc', 'webrtc'),
    ]

    def __init__(self):
        self._static_sip = asterisk_conf_dao.find_sip_general_settings()
        self._auth_data = asterisk_conf_dao.find_sip_authentication_settings()
        self._user_sip = list(asterisk_conf_dao.find_sip_user_settings())
        self._trunk = asterisk_conf_dao.find_sip_trunk_settings()
        self._general_settings_dict = {}

        for row in self._static_sip:
            self._general_settings_dict[row['var_name']] = row['var_val']

    def get(self, section):
        if section == 'global':
            return self._get_global()
        elif section == 'system':
            return self._get_system()
        elif section == 'transport-tcp':
            return self._get_transport_tcp()
        elif section == 'transport-udp':
            return self._get_transport_udp()
        elif section == 'transport-wss':
            return self._get_transport_wss()
        elif section == 'twilio-identify-template':
            return self._get_twilio_ident_template()
        elif section == 'wazo-general-aor':
            return self._get_general_aor_template()
        elif section == 'wazo-general-endpoint':
            return self._get_general_endpoint_template()
        elif section == 'wazo-general-registration':
            return self._get_general_registration_template()

    def get_trunk_sections(self):
        for registration_section in self._get_registration_sections(self._static_sip):
            yield registration_section

        for trunk_sip, twilio_incoming in self._trunk:
            for section in self._get_trunk(trunk_sip, twilio_incoming):
                yield section

    def get_user_sections(self):
        for user_sip, pickup_groups in self._user_sip:
            for section in self._get_user(user_sip, pickup_groups):
                yield section

    def _get_user(self, user_sip, pickup_groups):
        yield self._get_user_endpoint(user_sip, pickup_groups)
        yield self._get_user_aor(user_sip)
        yield self._get_user_auth(user_sip)

    def _get_trunk(self, trunk_sip, twilio_incoming):
        yield self._get_trunk_aor(trunk_sip)
        yield self._get_trunk_identify(trunk_sip, twilio_incoming)
        yield self._get_trunk_auth(trunk_sip)
        yield self._get_trunk_endpoint(trunk_sip)

    def _get_registration_sections(self, sip_general):
        for row in sip_general:
            if row['var_name'] != 'register':
                continue
            for section in self._convert_register(row['var_val']):
                yield section

    def _get_trunk_aor(self, trunk_sip):
        fields = [
            ('type', 'aor'),
        ]

        self._add_from_mapping(fields, self.sip_to_aor, trunk_sip.__dict__)
        for field in self._convert_host(trunk_sip):
            self._add_option(fields, field)

        return Section(
            name=trunk_sip.name,
            type_='section',
            templates=['wazo-general-aor'],
            fields=fields,
        )

    def _get_trunk_identify(self, trunk_sip, twilio_incoming):
        fields = [
            ('type', 'identify'),
            ('endpoint', trunk_sip.name),
            ('match', trunk_sip.host),
        ]

        if twilio_incoming:
            templates = ['twilio_identify_template']
        else:
            templates = None

        return Section(
            name=trunk_sip.name,
            type_='section',
            templates=templates,
            fields=fields,
        )

    def _get_user_aor(self, user_sip):
        fields = [
            ('type', 'aor'),
        ]

        self._add_from_mapping(fields, self.sip_to_aor, user_sip[0].__dict__)
        for field in self._convert_host(user_sip[0]):
            self._add_option(fields, field)

        if user_sip.mailbox and user_sip[0].subscribemwi == 'yes':
            self._add_option(fields, ('mailboxes', user_sip.mailbox))

        return Section(
            name=user_sip[0].name,
            type_='section',
            templates=['wazo-general-aor'],
            fields=fields,
        )

    def _get_user_auth(self, user_sip):
        fields = [
            ('type', 'auth'),
            ('username', user_sip[0].name),
            ('password', user_sip[0].secret),
        ]

        return Section(
            name=user_sip[0].name,
            type_='section',
            templates=None,
            fields=fields,
        )

    def _get_trunk_auth(self, trunk_sip):
        fields = [
            ('type', 'auth'),
            ('username', trunk_sip.name),
            ('password', trunk_sip.secret),
        ]

        return Section(
            name=trunk_sip.name,
            type_='section',
            templates=None,
            fields=fields,
        )

    def _get_user_endpoint(self, user_sip, pickup_groups):
        user_dict = user_sip[0].__dict__
        all_options = user_sip[0].all_options()

        for key, value in all_options:
            user_dict[key] = value

        fields = [
            ('type', 'endpoint'),
            ('context', user_dict['context']),
            ('aors', user_sip[0].name),
            ('set_var', 'XIVO_ORIGINAL_CALLER_ID={callerid}'.format(**user_dict)),
            ('set_var', 'TRANSFER_CONTEXT={}'.format(user_sip.context)),
            ('set_var', 'PICKUPMARK={}%{}'.format(user_sip.number, user_sip.context)),
            ('set_var', 'XIVO_USERID={}'.format(user_sip.user_id)),
            ('set_var', 'XIVO_USERUUID={}'.format(user_sip.uuid)),
            ('set_var', 'WAZO_CHANNEL_DIRECTION=from-wazo'),
        ]

        for key, value in all_options:
            if key in ('allow', 'disallow'):
                self._add_option(fields, (key, value))

        named_pickup_groups = ','.join(str(id) for id in pickup_groups.get('pickupgroup', []))
        if named_pickup_groups:
            self._add_option(fields, ('named_pickup_group', named_pickup_groups))

        named_call_groups = ','.join(str(id) for id in pickup_groups.get('callgroup', []))
        if named_call_groups:
            self._add_option(fields, ('named_call_group', named_call_groups))

        self._add_from_mapping(fields, self.sip_to_endpoint, user_dict)
        self._add_option(fields, self._convert_dtmfmode(user_dict))
        self._add_option(fields, self._convert_session_timers(user_dict))
        self._add_option(fields, self._convert_sendrpid(user_dict))
        self._add_option(fields, self._convert_encryption(user_dict))
        self._add_option(fields, self._convert_progressinband(user_dict))
        self._add_option(fields, self._convert_dtlsenable(user_dict))
        self._add_option(fields, self._convert_encryption_taglen(self._general_settings_dict))
        for pair in self._convert_nat(user_dict):
            self._add_option(fields, pair)
        for pair in self._convert_directmedia(user_dict):
            self._add_option(fields, pair)
        for pair in self._convert_recordonfeature(user_dict):
            self._add_option(fields, pair)
        for pair in self._convert_recordofffeature(user_dict):
            self._add_option(fields, pair)

        if user_sip.mailbox and user_dict.get('subscribemwi') != 'yes':
            self._add_option(fields, ('mailboxes', user_sip.mailbox))

        if user_dict.get('transport') == 'wss':
            self._add_option(fields, ('transport', 'transport-wss'))
        if user_dict.get('transport') == 'tcp':
            self._add_option(fields, ('transport', 'transport-tcp'))

        return Section(
            name=user_sip[0].name,
            type_='section',
            templates=['wazo-general-endpoint'],
            fields=fields,
        )

    def _get_trunk_endpoint(self, trunk_sip):
        trunk_dict = trunk_sip.__dict__
        all_options = trunk_sip.all_options()

        for key, value in all_options:
            trunk_dict[key] = value

        fields = [
            ('type', 'endpoint'),
            ('context', trunk_dict['context']),
            ('aors', trunk_sip.name),
            ('auth', trunk_sip.name),
            ('outbound_auth', trunk_sip.name),
        ]

        for key, value in all_options:
            if key in ('allow', 'disallow'):
                self._add_option(fields, (key, value))

        self._add_from_mapping(fields, self.sip_to_endpoint, trunk_dict)
        self._add_option(fields, self._convert_dtmfmode(trunk_dict))
        self._add_option(fields, self._convert_session_timers(trunk_dict))
        self._add_option(fields, self._convert_sendrpid(trunk_dict))
        self._add_option(fields, self._convert_encryption(trunk_dict))
        self._add_option(fields, self._convert_progressinband(trunk_dict))
        self._add_option(fields, self._convert_dtlsenable(trunk_dict))
        self._add_option(fields, self._convert_encryption_taglen(trunk_dict))
        for pair in self._convert_nat(trunk_dict):
            self._add_option(fields, pair)
        for pair in self._convert_directmedia(trunk_dict):
            self._add_option(fields, pair)

        return Section(
            name=trunk_sip.name,
            type_='section',
            templates=['wazo-general-endpoint'],
            fields=fields,
        )

    def _get_twilio_ident_template(self):
        fields = [
            ('type', 'identify'),
            ('match', '54.172.60.0'),
            ('match', '54.172.60.1'),
            ('match', '54.172.60.2'),
            ('match', '54.172.60.3'),
            ('match', '54.244.51.0'),
            ('match', '54.244.51.1'),
            ('match', '54.244.51.2'),
            ('match', '54.244.51.3'),
            ('match', '54.171.127.192'),
            ('match', '54.171.127.193'),
            ('match', '54.171.127.194'),
            ('match', '54.171.127.195'),
            ('match', '35.156.191.128'),
            ('match', '35.156.191.129'),
            ('match', '35.156.191.130'),
            ('match', '35.156.191.131'),
            ('match', '54.65.63.192'),
            ('match', '54.65.63.193'),
            ('match', '54.65.63.194'),
            ('match', '54.65.63.195'),
            ('match', '54.169.127.128'),
            ('match', '54.169.127.129'),
            ('match', '54.169.127.130'),
            ('match', '54.169.127.131'),
            ('match', '54.252.254.64'),
            ('match', '54.252.254.65'),
            ('match', '54.252.254.66'),
            ('match', '54.252.254.67'),
            ('match', '177.71.206.192'),
            ('match', '177.71.206.193'),
            ('match', '177.71.206.194'),
            ('match', '177.71.206.195'),
        ]

        return Section(
            name='twilio_identify_template',
            type_='template',
            templates=None,
            fields=fields,
        )

    def _get_general_aor_template(self):
        fields = [
            ('type', 'aor'),
        ]

        self._add_from_mapping(fields, self.sip_to_aor, self._general_settings_dict)

        return Section(
            name='wazo-general-aor',
            type_='template',
            templates=None,
            fields=fields,
        )

    def _get_general_endpoint_template(self):
        fields = [
            ('type', 'endpoint'),
            ('allow', '!all,ulaw'),
            ('transport', 'transport-udp'),
        ]

        self._add_from_mapping(fields, self.sip_to_endpoint, self._general_settings_dict)

        self._add_option(fields, self._convert_dtmfmode(self._general_settings_dict))
        self._add_option(fields, self._convert_session_timers(self._general_settings_dict))
        self._add_option(fields, self._convert_sendrpid(self._general_settings_dict))
        self._add_option(fields, self._convert_encryption(self._general_settings_dict))
        self._add_option(fields, self._convert_progressinband(self._general_settings_dict))
        self._add_option(fields, self._convert_dtlsenable(self._general_settings_dict))
        self._add_option(fields, self._convert_encryption_taglen(self._general_settings_dict))
        for pair in self._convert_nat(self._general_settings_dict):
            self._add_option(fields, pair)
        for pair in self._convert_directmedia(self._general_settings_dict):
            self._add_option(fields, pair)
        for pair in self._convert_recordonfeature(self._general_settings_dict):
            self._add_option(fields, pair)
        for pair in self._convert_recordofffeature(self._general_settings_dict):
            self._add_option(fields, pair)

        for row in self._static_sip:
            key = row['var_name']
            if key in ('allow', 'disallow'):
                self._add_option(fields, (key, row['var_val']))

        return Section(
            name='wazo-general-endpoint',
            type_='template',
            templates=None,
            fields=fields,
        )

    def _get_general_registration_template(self):
        fields = [
            ('type', 'registration'),
        ]

        self._add_from_mapping(fields, self.sip_general_to_register_tpl, self._general_settings_dict)
        outbound_proxy = self._general_settings_dict.get('outboundproxy')
        if outbound_proxy:
            self._add_option(fields, ('outbound_proxy', outbound_proxy))

        return Section(
            name='wazo-general-registration',
            type_='template',
            templates=None,
            fields=fields,
        )

    def _get_global(self):
        fields = [
            ('type', 'global'),
        ]

        self._add_from_mapping(fields, self.sip_general_to_global, self._general_settings_dict)

        return Section(
            name='global',
            type_='section',
            templates=None,
            fields=fields,
        )

    def _get_system(self):
        fields = [
            ('type', 'system'),
        ]

        self._add_from_mapping(fields, self.sip_general_to_system, self._general_settings_dict)

        return Section(
            name='system',
            type_='section',
            templates=None,
            fields=fields,
        )

    def _get_base_transport_fields(self, protocol):
        fields = [
            ('type', 'transport'),
            ('protocol', protocol),
        ]

        for row in self._static_sip:
            if row['var_name'] != 'localnet':
                continue
            fields.append(('local_net', row['var_val']))

        extern_ip = self._general_settings_dict.get('externip')
        extern_host = self._general_settings_dict.get('externhost')
        extern_signaling_address = extern_host or extern_ip
        if extern_signaling_address:
            fields.append(('external_signaling_address', extern_signaling_address))

        return fields

    def _get_base_udp_transport(self, protocol):
        fields = self._get_base_transport_fields(protocol)
        bind = self._general_settings_dict.get('udpbindaddr')
        port = self._general_settings_dict.get('bindport')
        if port:
            bind += ':{}'.format(port)

        fields.append(('bind', bind))

        return Section(
            name='transport-{}'.format(protocol),
            type_='section',
            templates=None,
            fields=fields,
        )

    def _get_transport_tcp(self):
        tcp_enabled = self._general_settings_dict.get('tcpenable')
        if tcp_enabled != 'yes':
            return

        fields = self._get_base_transport_fields('tcp')
        self._add_option(fields, self._convert_externtcpport(self._general_settings_dict))
        self._add_option(fields, self._convert_tcpbindaddr(self._general_settings_dict))

        return Section(
            name='transport-tcp',
            type_='section',
            templates=None,
            fields=fields,
        )

    def _get_transport_udp(self):
        return self._get_base_udp_transport('udp')

    def _get_transport_wss(self):
        if not self._general_settings_dict.get('websocket_enabled'):
            return

        return self._get_base_udp_transport('wss')

    def _add_from_mapping(self, fields, mapping, config):
        for sip_key, pjsip_key in mapping:
            value = config.get(sip_key)
            if not value:
                continue
            fields.append((pjsip_key, value))

    @staticmethod
    def _add_option(fields, pair):
        if not pair:
            return

        fields.append(pair)

    @staticmethod
    def _convert_directmedia(sip_config):
        val = sip_config.get('directmedia')
        if not val:
            return

        if 'yes' in val:
            yield 'direct_media', 'yes'
        if 'update' in val:
            yield 'direct_media_method', 'update'
        if 'outgoing' in val:
            yield 'direct_media_glare_mitigation', 'outgoing'
        if 'nonat' in val:
            yield 'disable_directed_media_on_nat', 'yes'
        if val == 'no':
            yield 'direct_media', 'no'

    @staticmethod
    def _convert_dtlsenable(sip_config):
        val = sip_config.get('dtlsenable')
        if val == 'yes':
            return 'media_encryption', 'dtls'

    @staticmethod
    def _convert_dtmfmode(sip_config):
        val = sip_config.get('dtmfmode')
        if not val:
            return

        key = 'dtmf_mode'
        if val == 'rfc2833':
            return key, 'rfc4733'
        elif val in ('inband', 'info'):
            return key, val

    @staticmethod
    def _convert_encryption(sip_config):
        val = sip_config.get('encryption')
        if val == 'yes':
            return 'media_encryption', 'sdes'

    @staticmethod
    def _convert_encryption_taglen(sip_config):
        val = sip_config.get('encryption_taglen')
        if val == 32:
            return 'srtp_tag_32', 'yes'

    @staticmethod
    def _convert_externtcpport(sip_config):
        val = sip_config.get('externtcpport')
        if val:
            return 'external_signaling_port', val

    @staticmethod
    def _convert_host(sip):
        host = sip.host
        if host == 'dynamic':
            yield ('remove_existing', 'yes')
            yield ('max_contacts', 1)
            return

        result = 'sip:'
        # More difficult case. The host will be either a hostname or
        # IP address and may or may not have a port specified. pjsip.conf
        # expects the contact to be a SIP URI.

        user = sip.username
        if user:
            result += user + '@'

        host_port = '{}:{}'.format(sip.host, sip.port or 5060)
        result += host_port

        yield ('contact', result)

    @staticmethod
    def _convert_nat(sip_config):
        val = sip_config.get('nat')
        if val == 'yes':
            yield 'rtp_symmetric', 'yes'
            yield 'rewrite_contact', 'yes'
        elif val == 'comedia':
            yield 'rtp_symmetric', 'yes'
        elif val == 'force_rport':
            yield 'force_rport', 'yes'
            yield 'rewrite_contact', 'yes'

    @staticmethod
    def _convert_progressinband(sip_config):
        val = sip_config.get('progressinband')
        if val in ('no', 'never'):
            return 'inband_progress', 'no'
        elif val == 'yes':
            return 'inband_progress', 'yes'

    @staticmethod
    def _convert_recordonfeature(sip_config):
        val = sip_config.get('recordonfeature')
        if not val:
            return
        if val == 'automixmon':
            yield 'one_touch_recording', 'yes'
        yield 'record_on_feature', val

    @staticmethod
    def _convert_recordofffeature(sip_config):
        val = sip_config.get('recordofffeature')
        if not val:
            return
        if val == 'automixmon':
            yield 'one_touch_recording', 'yes'
        yield 'record_off_feature', val

    @staticmethod
    def _convert_register(register_url):
        register = Registration(register_url)

        fields = register.registration_fields
        fields.append(('type', 'registration'))
        fields.append(('outbound_auth', register.auth_section))
        yield Section(
            name=register.section,
            type_='section',
            templates=['wazo-general-registration'],
            fields=fields,
        )

        fields = register.auth_fields
        fields.append(('type', 'auth'))
        yield Section(
            name=register.auth_section,
            type_='section',
            templates=None,
            fields=fields,
        )

    @staticmethod
    def _convert_sendrpid(sip_config):
        val = sip_config.get('sendrpid')
        if val in ('yes', 'rpid'):
            return 'send_rpid', 'yes'
        elif val == 'pai':
            return 'send_pai', 'yes'

    @staticmethod
    def _convert_session_timers(sip_config):
        val = sip_config.get('session-timers')
        if not val:
            return

        new_val = 'yes'
        if val == 'originate':
            new_val = 'always'
        elif val == 'accept':
            new_val = 'required'
        elif val == 'never':
            new_val = 'no'

        return 'timers', new_val

    @staticmethod
    def _convert_tcpbindaddr(sip_config):
        val = sip_config.get('tcpbindaddr')
        if not val:
            return

        host = val.rsplit(':', 1)[0] if ':' in val else val
        return 'bind', host


class PJSIPConfGenerator(object):

    def __init__(self, dependencies):
        self._config_file_generator = AsteriskConfFileGenerator()

    def generate(self):
        extractor = SipDBExtractor()

        global_sections = [
            extractor.get('global'),
            extractor.get('system'),
            extractor.get('transport-udp'),
            extractor.get('transport-wss'),
            extractor.get('transport-tcp'),
            extractor.get('wazo-general-aor'),
            extractor.get('wazo-general-endpoint'),
            extractor.get('wazo-general-registration'),
            extractor.get('twilio-identify-template'),
        ]
        user_sections = list(extractor.get_user_sections())
        trunk_sections = list(extractor.get_trunk_sections())

        return self._config_file_generator.generate(
            global_sections + user_sections + trunk_sections)
