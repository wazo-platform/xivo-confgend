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

    def __init__(self):
        self._static_sip = asterisk_conf_dao.find_sip_general_settings()
        self._auth_data = asterisk_conf_dao.find_sip_authentication_settings()
        self._user_sip = list(asterisk_conf_dao.find_sip_user_settings())
        self._trunk = asterisk_conf_dao.find_sip_trunk_settings()
        self._general_settings_dict = {}

        for row in self._static_sip:
            self._general_settings_dict[row['var_name']] = row['var_val']

        logger.critical('%s', self._static_sip)
        logger.critical('%s', self._auth_data)
        logger.critical('%s', self._user_sip)
        logger.critical('%s', self._trunk)
        logger.critical('%s', self._general_settings_dict)

    def get(self, section):
        if section == 'global':
            return self._get_global()
        elif section == 'system':
            return self._get_system()
        elif section == 'transport-udp':
            return self._get_transport_udp()
        elif section == 'transport-wss':
            return self._get_transport_wss()

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


class PJSIPConfGenerator(object):

    def __init__(self, dependencies):
        self._config_file_generator = AsteriskConfFileGenerator()

    def generate(self):
        extractor = SipDBExtractor()

        global_section = extractor.get('global')
        system_section = extractor.get('system')
        transport_udp_section = extractor.get('transport-udp')
        transport_wss_section = extractor.get('transport-wss')

        return self._config_file_generator.generate([section for section in [
            global_section,
            system_section,
            transport_udp_section,
            transport_wss_section,
        ] if section])
