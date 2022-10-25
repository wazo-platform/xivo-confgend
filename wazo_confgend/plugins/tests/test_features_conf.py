# -*- coding: utf-8 -*-
# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import unittest

from mock import patch
from wazo_confgend.plugins.features_conf import FeaturesConfGenerator
from wazo_confgend.generators.tests.util import assert_generates_config


class TestFeaturesConf(unittest.TestCase):

    def _new_conf(self, settings):
        with patch('xivo_dao.asterisk_conf_dao.find_features_settings'):
            conf = FeaturesConfGenerator()
            conf._settings = settings
            return conf

    def test_minimal_settings(self):
        settings = {
            'general_options': [],
            'featuremap_options': [],
            'applicationmap_options': [],
        }

        features_conf = self._new_conf(settings)

        assert_generates_config(features_conf, '''
            [general]

            [featuremap]

            [applicationmap]
        ''')

    def test_settings(self):
        settings = {
            'general_options': [('pickupexten', '*8')],
            'featuremap_options': [('blindxfer', '*1')],
            'applicationmap_options': [('toto', '*1')],
        }

        features_conf = self._new_conf(settings)

        assert_generates_config(features_conf, '''
            [general]
            pickupexten = *8

            [featuremap]
            blindxfer = *1

            [applicationmap]
            toto = *1
        ''')
