# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

    @patch('xivo_confgen.xivo.infos_services.get',
           Mock(return_value=MockedInfo(uuid='sentinel-uuid')))
    def test_uuid_yml(self):
        frontend = XivoFrontend()

        result = frontend.uuid_yml()
        print result

        expected = {
            'uuid': 'sentinel-uuid',
        }

        assert_that(yaml.load(result), equal_to(expected))
