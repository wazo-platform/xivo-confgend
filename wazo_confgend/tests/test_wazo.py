# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest
from collections import namedtuple
from unittest.mock import Mock, patch

import yaml
from hamcrest import assert_that, equal_to

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
