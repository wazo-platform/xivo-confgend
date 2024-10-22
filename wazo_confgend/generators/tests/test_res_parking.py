# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest
from unittest.mock import Mock, patch

from wazo_confgend.generators.res_parking import ResParkingConf
from wazo_confgend.generators.tests.util import assert_generates_config


class TestResParkingConf(unittest.TestCase):
    def _new_conf(self, parking_lots=None):
        with patch('xivo_dao.resources.parking_lot.dao.find_all_by'):
            conf = ResParkingConf()
            conf._parking_lots = parking_lots or []
            return conf

    def test_no_settings(self):
        res_parking_conf = self._new_conf()

        assert_generates_config(
            res_parking_conf,
            '''
            [default]
            context = wazo-disabled
            ''',
        )

    def test_parking_lots(self):
        parking_lots = [
            Mock(
                id=1,
                slots_start='801',
                slots_end='850',
                extensions=[Mock(exten='800', context='default')],
                music_on_hold='music_class',
                timeout=60,
            )
        ]

        res_parking_conf = self._new_conf(parking_lots)

        assert_generates_config(
            res_parking_conf,
            '''
            [default]
            context = wazo-disabled

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
        ''',
        )

    def test_parking_lots_with_none_values(self):
        parking_lots = [
            Mock(
                id=1,
                slots_start='801',
                slots_end='850',
                extensions=[Mock(exten='800', context='default')],
                music_on_hold=None,
                timeout=None,
            )
        ]

        res_parking_conf = self._new_conf(parking_lots)

        assert_generates_config(
            res_parking_conf,
            '''
            [default]
            context = wazo-disabled

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
        ''',
        )
