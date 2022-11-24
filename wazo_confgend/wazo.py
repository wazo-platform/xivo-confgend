# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import yaml

from xivo_dao.resources.infos import dao as infos_dao


class WazoFrontend(object):
    def uuid_yml(self):
        content = {'uuid': infos_dao.get().uuid}
        return yaml.safe_dump(content)
