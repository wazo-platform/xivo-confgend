# -*- coding: utf-8 -*-
# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import textwrap

from xivo_dao import init_db_from_config
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.alchemy.provisioning import Provisioning
from xivo_dao.alchemy.netiface import Netiface


class ProvdNetworkConfGenerator(object):

    def __init__(self, dependencies):
        init_db_from_config(dependencies['config'])

    def get_provd_net4_ip(self, session):
        result = session.query(Provisioning.net4_ip).first()
        if not result:
            return
        return result.net4_ip

    def get_netiface_net4_ip(self, session):
        result = session.query(Netiface.address).filter(Netiface.networktype == 'voip').first()
        if not result:
            return
        return result.address

    def generate(self):
        with session_scope(read_only=True) as session:
            address = self.get_provd_net4_ip(session) or self.get_netiface_net4_ip(session)

        if not address:
            return ''

        return textwrap.dedent('''\
            general:
                external_ip: {}
        '''.format(address))
