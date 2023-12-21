# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import yaml
from xivo_dao import init_db_from_config
from xivo_dao.alchemy.netiface import Netiface
from xivo_dao.alchemy.provisioning import Provisioning
from xivo_dao.helpers.db_utils import session_scope


class ProvdNetworkConfGenerator:
    def __init__(self, dependencies):
        init_db_from_config(dependencies['config'])

    def get_provd_net4_ip(self, session):
        result = session.query(Provisioning.net4_ip).first()
        if not result:
            return
        return result.net4_ip

    def get_netiface_net4_ip(self, session):
        result = (
            session.query(Netiface.address)
            .filter(Netiface.networktype == 'voip')
            .first()
        )
        if not result:
            return
        return result.address

    def get_provd_http_port(self, session):
        result = session.query(Provisioning.http_port).first()
        if not result:
            return
        return result.http_port

    def get_provd_http_base_url(self, session):
        result = session.query(Provisioning.http_base_url).first()
        if not result:
            return
        return result.http_base_url

    def generate_http_base_url(self, session):
        http_ip = self.get_provd_net4_ip(session)
        if not http_ip:
            http_ip = self.get_netiface_net4_ip(session)
        if not http_ip:
            return

        http_port = self.get_provd_http_port(session)
        if not http_port:
            return f'http://{http_ip}'

        return f'http://{http_ip}:{http_port}'

    def generate(self):
        config = {}
        with session_scope(read_only=True) as session:
            http_base_url = self.get_provd_http_base_url(session)
            if not http_base_url:
                http_base_url = self.generate_http_base_url(session)

            if http_base_url:
                config['general'] = {'advertised_http_url': http_base_url}

        return yaml.safe_dump(config, default_flow_style=False)
