# -*- coding: utf-8 -*-

# Copyright 2015-2016 The Wazo Authors  (see the AUTHORS file)
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

from mock import patch, Mock
from xivo_confgen.generators.res_parking import ResParkingConf
from xivo_confgen.generators.tests.util import assert_generates_config


class TestResParkingConf(unittest.TestCase):

    def _new_conf(self, settings, parking_lots=None):
        with patch('xivo_dao.asterisk_conf_dao.find_parking_settings'), \
                patch('xivo_dao.resources.parking_lot.dao.find_all_by'):
            conf = ResParkingConf()
            conf._settings = settings
            conf._parking_lots = parking_lots or []
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

    def test_settings_with_parking_lots(self):
        settings = {
            'general_options': [],
            'parking_lots': []
        }
        parking_lots = [Mock(id=1,
                             slots_start='801',
                             slots_end='850',
                             extensions=[Mock(exten='800', context='default')],
                             music_on_hold='music_class',
                             timeout=60)]

        res_parking_conf = self._new_conf(settings, parking_lots)

        assert_generates_config(res_parking_conf, '''
            [general]

            [parkinglot-1]
            parkext = 800
            context = default
            parkedmusicclass = music_class
            parkpos = 801-850
            parkingtime = 60
            findslot = next
            parkext_exclusive = yes
            parkinghints = yes
            comebacktoorigin = yes
            parkedplay = caller
            parkedcalltransfers = no
            parkedcallreparking = no
            parkedcallhangup = no
            parkedcallrecording = no
        ''')

    def test_parking_lots_with_none_values(self):
        settings = {
            'general_options': [],
            'parking_lots': []
        }
        parking_lots = [Mock(id=1,
                             slots_start='801',
                             slots_end='850',
                             extensions=[Mock(exten='800', context='default')],
                             music_on_hold=None,
                             timeout=None)]

        res_parking_conf = self._new_conf(settings, parking_lots)

        assert_generates_config(res_parking_conf, '''
            [general]

            [parkinglot-1]
            parkext = 800
            context = default
            parkedmusicclass = 
            parkpos = 801-850
            parkingtime = 0
            findslot = next
            parkext_exclusive = yes
            parkinghints = yes
            comebacktoorigin = yes
            parkedplay = caller
            parkedcalltransfers = no
            parkedcallreparking = no
            parkedcallhangup = no
            parkedcallrecording = no
        ''')
