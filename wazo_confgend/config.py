# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy
from xivo.xivo_logging import get_log_level_by_name

_DEFAULT_CONFIG = {
    'config_file': '/etc/wazo-confgend/config.yml',
    'extra_config_files': '/etc/wazo-confgend/conf.d',
    'debug': False,
    'log_level': 'info',
    'log_filename': '/var/log/wazo-confgend.log',
    'cache': '/var/cache/wazo-confgend',
    'listen_address': '127.0.0.1',
    'listen_port': 8669,
    'db_uri': 'postgresql://asterisk:proformatique@localhost/asterisk?application_name=wazo-confgend',
    'templates': {'contextsconf': '/etc/wazo-confgend/templates/contexts.conf'},
    'plugins': {},
}


def load():
    file_config = read_config_file_hierarchy(_DEFAULT_CONFIG)
    reinterpreted_config = _get_reinterpreted_raw_values(
        ChainMap(file_config, _DEFAULT_CONFIG)
    )
    config = ChainMap(reinterpreted_config, file_config, _DEFAULT_CONFIG)
    return config


def _get_reinterpreted_raw_values(config):
    result = {}

    if config.get('listen_address') == '*':
        result = {'listen_address': ''}

    log_level = config.get('log_level')
    if log_level:
        result['log_level'] = get_log_level_by_name(log_level)

    return result
