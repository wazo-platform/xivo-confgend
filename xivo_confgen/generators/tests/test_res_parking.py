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

from mock import patch
from xivo_confgen.generators.res_parking import ResParkingConf
from xivo_confgen.generators.tests.util import assert_generates_config


class TestResParkingConf(unittest.TestCase):

    def _new_conf(self, settings):
        with patch('xivo_dao.asterisk_conf_dao.find_parking_settings'):
            conf = ResParkingConf()
            conf._settings = settings
            return conf

    def test_minimal_settings(self):
        settings = {
            'general_options': [],
            'parking_lots': [],
        }

        res_parking_conf = self._new_conf(settings)

        assert_generates_config(res_parking_conf, '''
            [general]
        ''')

    def test_settings(self):
        settings = {
            'general_options': [(u'parkeddynamic', u'no')],
            'parking_lots': [{
                'name': u'default',
                'options': [(u'parkext', u'700')]
            }],
        }

        res_parking_conf = self._new_conf(settings)

        assert_generates_config(res_parking_conf, '''
            [general]
            parkeddynamic = no

            [default]
            parkext = 700
        ''')
