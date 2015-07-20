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

from xivo_dao import directory_dao


class DirdFrontend(object):

    confd_api_version = '1.1'
    confd_default_timeout = 4
    phonebook_default_timeout = 4
    supported_types = ['phonebook', 'xivo']

    def sources_yml(self):
        sources = dict(self._format_source(source)
                       for source in directory_dao.get_all_sources()
                       if source['type'] in self.supported_types)
        return yaml.dump({'sources': sources})

    def _format_source(self, source):
        name = source['name']
        type_ = source['type']
        config = {
            'type': type_,
            'name': name,
            'searched_columns': source['searched_columns'],
            'format_columns': source['format_columns'],
        }

        if type_ == 'xivo':
            config.update(self._format_xivo_source(source))
        elif type_ == 'phonebook':
            config.update(self._format_phonebook_source(source))

        return name, config

    def _format_phonebook_source(self, source):
        return {'phonebook_url': source['uri'],
                'phonebook_timeout': 4}

    def _format_xivo_source(self, source):
        return {
            'unique_column': 'id',
            'confd_config': self._format_confd_config(source['uri']),
        }

    def _format_confd_config(self, url):
        scheme, _, end = url.partition('://')
        host, _, port = end.partition(':')

        return {
            'https': scheme == 'https',
            'host': host,
            'port': int(port),
            'timeout': self.confd_default_timeout,
            'version': self.confd_api_version,
        }
