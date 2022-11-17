# -*- coding: utf-8 -*-
# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest
import yaml

from hamcrest import assert_that, equal_to
from mock import patch

from ..phoned import PhonedFrontend


class TestDirdFrontend(unittest.TestCase):
    @patch('wazo_confgend.phoned.phone_access_dao')
    def test_config_yml(self, mock_phone_access_dao):
        authorized_subnets = ['169.254.0.0/16']
        mock_phone_access_dao.get_authorized_subnets.return_value = authorized_subnets
        frontend = PhonedFrontend()

        result = frontend.config_yml()

        expected = {'rest_api': {'authorized_subnets': authorized_subnets}}

        assert_that(yaml.safe_load(result), equal_to(expected))
