# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import yaml

from xivo_dao import cti_displays_dao, directory_dao


class _AssociationGenerator(object):

    def generate(self):
        raw = cti_displays_dao.get_profile_configuration()
        return {profile: config['display']
                for profile, config in raw.iteritems()}

class _DisplayGenerator(object):

    _fields = ['title', 'type', 'default', 'field']

    def generate(self):
        raw = cti_displays_dao.get_config()
        return  {name: self._format_columns(column)
                 for name, column in raw.iteritems()}

    def _format_columns(self, column_configs):
        keys = sorted(column_configs.iterkeys())
        return [self._format_line(column_configs[key]) for key in keys]

    def _format_line(self, line_config):
        return dict(zip(self._fields, line_config))


class _LookupServiceGenerator(object):

    _default_sources = ['personal']

    def __init__(self, profile_configuration):
        self._profile_config = profile_configuration

    def generate(self):
        return {profile: {'sources': conf['sources'] + self._default_sources}
                for profile, conf in self._profile_config.iteritems()}


class _FavoritesServiceGenerator(_LookupServiceGenerator):
    pass


class DirdFrontend(object):

    confd_api_version = '1.1'
    confd_default_timeout = 4
    phonebook_default_timeout = 4
    supported_types = ['csv', 'csv_ws', 'ldap', 'phonebook', 'xivo']

    def services_yml(self):
        profile_config = cti_displays_dao.get_profile_configuration()
        lookups = _LookupServiceGenerator(profile_config).generate()
        favorites = _FavoritesServiceGenerator(profile_config).generate()

        return yaml.safe_dump({'services': {'lookup': lookups,
                                       'favorites': favorites}})

    def sources_yml(self):
        sources = dict(self._format_source(source)
                       for source in directory_dao.get_all_sources()
                       if source['type'] in self.supported_types)
        return yaml.safe_dump({'sources': sources})

    def views_yml(self):
        displays = _DisplayGenerator().generate()
        associations = _AssociationGenerator().generate()

        views_section = {'views': {'displays': displays,
                                   'profile_to_display': associations}}

        return yaml.safe_dump(views_section)

    def _format_source(self, source):
        name = source['name']
        type_ = source['type']
        config = {'type': type_,
                  'name': name,
                  'searched_columns': source['searched_columns'],
                  'format_columns': source['format_columns']}

        if type_ == 'xivo':
            config.update(self._format_xivo_source(source))
        elif type_ == 'phonebook':
            config.update(self._format_phonebook_source(source))
        elif type_ == 'csv':
            config.update(self._format_csv_source(source))
        elif type_ == 'csv_ws':
            config.update(self._format_csv_ws_source(source))
        elif type_ == 'ldap':
            config.update(self._format_ldap_source(source))

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
        }

    def _format_phonebook_source(self, source):
        return {'phonebook_url': source['uri'],
                'phonebook_timeout': 4}

    def _format_xivo_source(self, source):
        return {'unique_column': 'id',
                'confd_config': self._format_confd_config(source['uri'])}

    def _format_confd_config(self, url):
        scheme, _, end = url.partition('://')
        host, _, port = end.partition(':')

        return {'https': scheme == 'https',
                'host': host,
                'port': int(port),
                'timeout': self.confd_default_timeout,
                'version': self.confd_api_version}
