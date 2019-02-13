# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml
import unittest

from collections import namedtuple
from hamcrest import assert_that
from hamcrest import equal_to
from mock import Mock
from mock import patch

from ..xivo import XivoFrontend

MockedInfo = namedtuple('MockedInfo', ['uuid'])


class TestUUIDyml(unittest.TestCase):

    @patch('xivo_confgen.xivo.infos_dao.get',
           Mock(return_value=MockedInfo(uuid='sentinel-uuid')))
    def test_uuid_yml(self):
        frontend = XivoFrontend()

        result = frontend.uuid_yml()

        expected = {
            'uuid': 'sentinel-uuid',
        }

        assert_that(yaml.load(result), equal_to(expected))
