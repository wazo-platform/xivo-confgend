# -*- coding: utf-8 -*-
# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import yaml
import unittest

from collections import namedtuple
from hamcrest import assert_that
from hamcrest import equal_to
from mock import Mock
from mock import patch

from ..wazo import WazoFrontend

MockedInfo = namedtuple('MockedInfo', ['uuid'])


class TestUUIDyml(unittest.TestCase):
    @patch(
        'wazo_confgend.wazo.infos_dao.get',
        Mock(return_value=MockedInfo(uuid='sentinel-uuid')),
    )
    def test_uuid_yml(self):
        frontend = WazoFrontend()

        result = frontend.uuid_yml()

        expected = {
            'uuid': 'sentinel-uuid',
        }

        assert_that(yaml.safe_load(result), equal_to(expected))
