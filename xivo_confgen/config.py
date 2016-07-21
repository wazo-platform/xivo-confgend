# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
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

from __future__ import absolute_import

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy


_DEFAULT_CONFIG = {
    'config_file': '/etc/xivo-confgend/config.yml',
    'extra_config_files': '/etc/xivo-confgend/conf.d',
    'cache': '/var/lib/xivo-confgend',
    'listen_address': '127.0.0.1',
    'listen_port': 8669,
    'db_uri': 'postgresql://asterisk:proformatique@localhost/asterisk',
    'templates': {'contextsconf': '/etc/xivo-confgend/templates/contexts.conf'},
}


def load():
    file_config = read_config_file_hierarchy(_DEFAULT_CONFIG)
    reinterpreted_config = _get_reinterpreted_raw_values(ChainMap(file_config, _DEFAULT_CONFIG))
    config = ChainMap(reinterpreted_config, file_config, _DEFAULT_CONFIG)
    return config


def _get_reinterpreted_raw_values(config):
    if config.get('listen_address') == '*':
        return {'listen_address': ''}
    else:
        return {}
