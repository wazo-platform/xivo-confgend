# -*- coding: utf-8 -*-
# Copyright 2011-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later



from xivo_dao import asterisk_conf_dao

from wazo_confgend.generators.util import AsteriskFileWriter


def write_allow_rules(allowed, ast_writer):
    ast_writer.write_option('disallow', 'all')
    for value in allowed.split(','):
        ast_writer.write_option('allow', value)


class IaxConf(object):
    def __init__(self):
        self._general_settings = asterisk_conf_dao.find_iax_general_settings()
        self._call_limit_settings = asterisk_conf_dao.find_iax_calllimits_settings()
        self._trunk_settings = asterisk_conf_dao.find_iax_trunk_settings()

    def generate(self, output):
        ast_writer = AsteriskFileWriter(output)
        self._generate_general(ast_writer)
        self._generate_call_limits(ast_writer)
        for trunk in self._trunk_settings:
            self._generate_trunk(trunk, ast_writer)

    def _generate_general(self, ast_writer):
        ast_writer.write_section('general')

        for item in self._general_settings:
            name, value = item['var_name'], item['var_val']
            if value is None:
                continue

            if name == 'register':
                ast_writer.write_object_option(name, value)

            elif name not in ['allow', 'disallow']:
                ast_writer.write_option(name, value)

            elif name == 'allow':
                write_allow_rules(value, ast_writer)

    def _generate_call_limits(self, ast_writer):
        if self._call_limit_settings:
            ast_writer.write_section('callnumberlimits')
            for auth in self._call_limit_settings:
                name = '{}/{}'.format(auth['destination'], auth['netmask'])
                ast_writer.write_option(name, auth['calllimits'])

    def _generate_trunk(self, trunk, ast_writer):
        ast_writer.write_section(trunk.name)

        exclude_options = ('id', 'name', 'protocol', 'category', 'commented', 'disallow')
        for k, v in trunk.all_options(exclude=exclude_options):
            if v in (None, ''):
                continue

            if isinstance(v, str):
                v = v.encode('utf8')

            if k == 'allow':
                write_allow_rules(v, ast_writer)
            else:
                ast_writer.write_option(k, v)
