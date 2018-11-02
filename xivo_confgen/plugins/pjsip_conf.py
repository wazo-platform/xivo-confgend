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

    def _get_global(self):
        fields = [
            ('type', 'global'),
        ]

        for sip_key, pjsip_key in self.sip_general_to_global:
            value = self._general_settings_dict.get(sip_key)
            if not value:
                continue
            fields.append((pjsip_key, value))

        return Section(
            name='global',
            type_='section',
            templates=None,
            fields=fields,
        )


class PJSIPConfGenerator(object):

    def __init__(self, dependencies):
        self._config_file_generator = AsteriskConfFileGenerator()

    def generate(self):
        extractor = SipDBExtractor()

        global_section = extractor.get('global')

        return self._config_file_generator.generate([global_section])
