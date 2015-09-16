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

import unittest
import yaml

from hamcrest import assert_that, equal_to
from mock import patch

from ..dird_phoned import DirdPhonedFrontend


class TestDirdFrontend(unittest.TestCase):

    @patch('xivo_confgen.dird_phoned.phone_access_dao')
    def test_config_yml(self, mock_phone_access_dao):
        authorized_subnets = ['169.254.0.0/16']
        mock_phone_access_dao.get_authorized_subnets.return_value = authorized_subnets
        frontend = DirdPhonedFrontend()

        result = frontend.config_yml()

        expected = {
            'rest_api': {
                'authorized_subnets': authorized_subnets
            }
        }

        assert_that(yaml.load(result), equal_to(expected))
