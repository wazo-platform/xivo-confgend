# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest
from unittest.mock import Mock, patch

from wazo_confgend.generators.res_parking import ResParkingConf
from wazo_confgend.generators.tests.util import assert_generates_config


class TestResParkingConf(unittest.TestCase):
    def _new_conf(self, settings, parking_lots=None):
        with patch('xivo_dao.asterisk_conf_dao.find_parking_settings'), patch(
            'xivo_dao.resources.parking_lot.dao.find_all_by'
        ):
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

        assert_generates_config(
            res_parking_conf,
            '''
            [general]
        ''',
        )

    def test_settings(self):
        settings = {
            'general_options': [('parkeddynamic', 'no')],
            'parking_lots': [{'name': 'default', 'options': [('parkext', '700')]}],
        }

        res_parking_conf = self._new_conf(settings)

        assert_generates_config(
            res_parking_conf,
            '''
            [general]
            parkeddynamic = no

            [default]
            parkext = 700
        ''',
        )

    def test_settings_with_parking_lots(self):
        settings = {'general_options': [], 'parking_lots': []}
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

        res_parking_conf = self._new_conf(settings, parking_lots)

        assert_generates_config(
            res_parking_conf,
            '''
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
        ''',
        )

    def test_parking_lots_with_none_values(self):
        settings = {'general_options': [], 'parking_lots': []}
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

        res_parking_conf = self._new_conf(settings, parking_lots)

        assert_generates_config(
            res_parking_conf,
            '''
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
        ''',
        )
