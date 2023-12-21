# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import yaml
from xivo_dao import phone_access_dao


class PhonedFrontend:
    def config_yml(self):
        authorized_subnets = phone_access_dao.get_authorized_subnets()
        generator = _ConfigGenerator(authorized_subnets)

        return yaml.safe_dump(generator.generate())


class _ConfigGenerator:
    def __init__(self, authorized_subnets):
        self._authorized_subnets = authorized_subnets

    def generate(self):
        return {'rest_api': {'authorized_subnets': self._authorized_subnets}}
