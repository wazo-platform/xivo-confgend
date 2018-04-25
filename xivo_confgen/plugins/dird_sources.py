# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import yaml

from xivo_dao import (
    cti_context_dao,
    cti_main_dao,
    directory_dao,
)


class SourceGenerator(object):

    def __init__(self, dependencies):
        pass

    def generate(self):
        raw_sources = directory_dao.get_all_sources()
        if bool(cti_main_dao.get_config()['main']['context_separation']):
            generator = _ContextSeparatedSourceGenerator(raw_sources)
        else:
            generator = _NoContextSeparationSourceGenerator(raw_sources)

        return yaml.safe_dump({'sources': generator.generate()})


class _ContextSeparatedMixin(object):

    _context_separated_types = ['xivo']

    def source_name(self, profile, name, type_):
        if type_ in self._context_separated_types:
            return '{}_{}'.format(name, profile)
        return name


class _NoContextSeparationSourceGenerator(object):

    confd_api_version = '1.1'
    confd_default_timeout = 4
    phonebook_default_timeout = 4
    supported_types = ['csv', 'csv_ws', 'ldap', 'xivo', 'dird_phonebook']

    def __init__(self, raw_sources):
        self._raw_sources = raw_sources

    def generate(self):
        return dict(self._format_source(source)
                    for source in self._raw_sources
                    if source['type'] in self.supported_types)

    def _format_source(self, source):
        name = source['name']
        type_ = source['type']
        config = {'type': type_,
                  'name': name,
                  'searched_columns': source['searched_columns'],
                  'first_matched_columns': source['first_matched_columns'],
                  'format_columns': source['format_columns']}

        if type_ == 'xivo':
            config.update(self._format_xivo_source(source))
        elif type_ == 'csv':
            config.update(self._format_csv_source(source))
        elif type_ == 'csv_ws':
            config.update(self._format_csv_ws_source(source))
        elif type_ == 'ldap':
            config.update(self._format_ldap_source(source))
        elif type_ == 'dird_phonebook':
            config.update(self._format_dird_phonebook_source(source))

        return name, config

    def _format_csv_source(self, source):
        _, _, filename = source['uri'].partition('file://')
        return {'file': filename,
                'separator': source['delimiter']}

    def _format_csv_ws_source(self, source):
        return {'delimiter': source['delimiter'],
                'lookup_url': source['uri']}

    def _format_ldap_source(self, source):
        return {
            'ldap_uri': source['ldap_uri'],
            'ldap_username': source['ldap_username'],
            'ldap_password': source['ldap_password'],
            'ldap_base_dn': source['ldap_base_dn'],
            'ldap_custom_filter': source['ldap_custom_filter'],
        }

    def _format_xivo_source(self, source):
        return {'unique_column': 'id',
                'confd_config': self._format_confd_config(source)}

    def _format_confd_config(self, source):
        scheme, _, end = source['uri'].partition('://')
        host, _, port = end.partition(':')
        verify_certificate = self._format_confd_verify_certificate(source)

        config = {
            'https': scheme == 'https',
            'host': host,
            'timeout': self.confd_default_timeout,
            'version': self.confd_api_version,
            'verify_certificate': verify_certificate
        }
        if port:
            config['port'] = int(port)
        if source['xivo_username'] and source['xivo_password']:
            config['username'] = source['xivo_username']
            config['password'] = source['xivo_password']

        return config

    def _format_confd_verify_certificate(self, source):
        if source['xivo_verify_certificate']:
            if source['xivo_custom_ca_path']:
                return source['xivo_custom_ca_path']
            else:
                return True
        else:
            return False

    def _format_dird_phonebook_source(self, source):
        return {'tenant': source['dird_tenant'],
                'phonebook_name': source['dird_phonebook'],
                'db_uri': source['uri']}


class _ContextSeparatedSourceGenerator(_NoContextSeparationSourceGenerator, _ContextSeparatedMixin):

    def __init__(self, *args, **kwargs):
        super(_ContextSeparatedSourceGenerator, self).__init__(*args, **kwargs)
        self._profiles = cti_context_dao.get_context_names()

    def generate(self):
        raw_result = super(_ContextSeparatedSourceGenerator, self).generate()

        results = {}
        for name, config in raw_result.iteritems():
            if config['type'] not in self._context_separated_types:
                results[name] = config
                continue
            for profile in self._profiles:
                new_name = self.source_name(profile, name, config['type'])
                results[new_name] = dict(config)
                results[new_name]['name'] = new_name
                results[new_name]['extra_search_params'] = {'context': profile}
        return results
