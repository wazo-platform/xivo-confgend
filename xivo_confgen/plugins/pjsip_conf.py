# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from collections import namedtuple

from xivo_dao import asterisk_conf_dao

logger = logging.getLogger(__name__)

Section = namedtuple('Section', ['name', 'type_', 'templates', 'fields'])


class AsteriskConfFileGenerator(object):

    def generate(self, data):
        lines = []

        for section, type_, templates, fields in data:
            fields = fields or []
            header = self._build_header(section, type_, templates)

            lines.append(header)
            for key, value in fields:
                lines.append('{} = {}'.format(key, value))
            lines.append('')

        return '\n'.join(lines)

    def _build_header(self, section, type_, templates):
        templates = templates or []
        in_parens = []

        if type_ == 'extends':
            in_parens.append('+')
        elif type_ == 'template':
            in_parens.append('!')

        for template in templates:
            in_parens.append(template)

        end = '({})'.format(','.join(in_parens)) if in_parens else ''
        return '[{}]{}'.format(section, end)


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
    sip_to_aor = [
        ('qualifyfreq', 'qualify_frequency'),
        ('maxexpiry', 'maximum_expiration'),
        ('minexpiry', 'minimum_expiration'),
        ('defaultexpiry', 'default_expiration'),
    ]
    sip_general_to_endpoint_tpl = [
        ('icesupport', 'ice_support'),
        ('autoframing', 'use_ptime'),
        ('outboundproxy', 'outbound_proxy'),
        ('mohsuggest', 'moh_suggest'),
        ('session-minse', 'timers_min_se'),
        ('session-expires', 'timers_sess_expires'),
        ('fromdomain', 'from_domain'),
        ('sdpowner', 'sdp_owner'),
        ('sdpsession', 'sdp_session'),
        ('language', 'language'),
    ]

    def __init__(self):
        self._static_sip = asterisk_conf_dao.find_sip_general_settings()
        self._auth_data = asterisk_conf_dao.find_sip_authentication_settings()
        self._user_sip = list(asterisk_conf_dao.find_sip_user_settings())
        self._trunk = asterisk_conf_dao.find_sip_trunk_settings()
        self._general_settings_dict = {}

        for row in self._static_sip:
            self._general_settings_dict[row['var_name']] = row['var_val']

        logger.critical('AUTH DATA')
        logger.critical('%s', self._auth_data)
        logger.critical('USER SIP')
        logger.critical('%s', self._user_sip)
        logger.critical('TRUNK SIP')
        logger.critical('%s', self._trunk)

    def get(self, section):
        if section == 'global':
            return self._get_global()
        elif section == 'system':
            return self._get_system()
        elif section == 'transport-udp':
            return self._get_transport_udp()
        elif section == 'transport-wss':
            return self._get_transport_wss()
        elif section == 'wazo-general-aor':
            return self._get_general_aor_template()
        elif section == 'wazo-general-endpoint':
            return self._get_general_endpoint_template()

    def get_user_sections(self):
        for user_sip, pickup_groups in self._user_sip:
            logger.critical('Usersip: %s', user_sip)
            logger.critical('pickup: %s', pickup_groups)
            for section in self._get_user(user_sip, pickup_groups):
                yield section

    def _get_user(self, user_sip, pickup_groups):
        yield self._get_user_endpoint(user_sip, pickup_groups)
        yield self._get_user_aor(user_sip)
        yield self._get_user_auth(user_sip)

    def _get_user_aor(self, user_sip):
        fields = [
            ('type', 'aor'),
        ]

        self._add_from_mapping(fields, self.sip_to_aor, user_sip[0].__dict__)
        # TODO check mailboxes AOR vs endpoint
        host = user_sip[0].host
        if host == 'dynamic':
            self._add_option(fields, ('max_contacts', 1))
        else:
            # TODO add the contact field
            pass

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

    def _get_user_endpoint(self, user_sip, pickup_groups):
        fields = [
            ('type', 'endpoint'),
        ]

        return Section(
            name=user_sip[0].name,
            type_='section',
            templates=['wazo-general-endpoint'],
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
        ]

        self._add_from_mapping(fields, self.sip_general_to_endpoint_tpl, self._general_settings_dict)

        self._add_option(fields, self._convert_dtmfmode(self._general_settings_dict))
        self._add_option(fields, self._convert_session_timers(self._general_settings_dict))
        self._add_option(fields, self._convert_sendrpid(self._general_settings_dict))
        self._add_option(fields, self._convert_encryption(self._general_settings_dict))
        for pair in self._convert_nat(self._general_settings_dict):
            self._add_option(fields, pair)
        for pair in self._convert_directmedia(self._general_settings_dict):
            self._add_option(fields, pair)

        return Section(
            name='wazo-general-endpoint',
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

    def _get_transport(self, protocol):
        fields = [
            ('type', 'transport'),
            ('protocol', protocol),
        ]

        bind = self._general_settings_dict.get('udpbindaddr')
        port = self._general_settings_dict.get('bindport')
        if port:
            bind += ':{}'.format(port)

        fields.append(('bind', bind))

        extern_ip = self._general_settings_dict.get('externip')
        extern_host = self._general_settings_dict.get('externhost')
        extern_signaling_address = extern_host or extern_ip
        if extern_signaling_address:
            fields.append(('external_signaling_address', extern_signaling_address))

        for row in self._static_sip:
            if row['var_name'] != 'localnet':
                continue
            fields.append(('local_net', row['var_val']))

        return Section(
            name='transport-{}'.format(protocol),
            type_='section',
            templates=None,
            fields=fields,
        )

    def _get_transport_udp(self):
        return self._get_transport('udp')

    def _get_transport_wss(self):
        if not self._general_settings_dict.get('websocket_enabled'):
            return

        return self._get_transport('wss')

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
    def _convert_dtmfmode(sip_config):
        val = sip_config.get('dtmfmode')
        if not val:
            return

        key = 'dtmf_mode'
        if val == 'rfc2833':
            return key, 'rfc4733'
        else:
            return key, val

    @staticmethod
    def _convert_encryption(sip_config):
        val = sip_config.get('encryption')
        if val == 'yes':
            return 'media_encryption', 'sdes'

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
            return 'progress_inband', 'no'
        elif val == 'yes':
            return 'progress_inband', 'yes'

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


class PJSIPConfGenerator(object):

    def __init__(self, dependencies):
        self._config_file_generator = AsteriskConfFileGenerator()

    def generate(self):
        extractor = SipDBExtractor()

        global_section = extractor.get('global')
        system_section = extractor.get('system')
        transport_udp_section = extractor.get('transport-udp')
        transport_wss_section = extractor.get('transport-wss')
        general_aor_tpl = extractor.get('wazo-general-aor')
        general_endpoint_tpl = extractor.get('wazo-general-endpoint')
        user_sections = list(extractor.get_user_sections())

        return self._config_file_generator.generate([section for section in [
            global_section,
            system_section,
            transport_udp_section,
            transport_wss_section,
            general_aor_tpl,
            general_endpoint_tpl,
        ] if section] + user_sections)
