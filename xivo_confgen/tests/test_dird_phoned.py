# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
