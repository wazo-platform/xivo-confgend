# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml

from xivo_dao.resources.infos import dao as infos_dao


class XivoFrontend(object):

    def uuid_yml(self):
        content = {'uuid': infos_dao.get().uuid}
        return yaml.safe_dump(content)
