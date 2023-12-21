# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest
from unittest.mock import patch

from wazo_confgend.generators.tests.util import assert_config_equal
from wazo_confgend.plugins.features_conf import FeaturesConfGenerator


class TestFeaturesConf(unittest.TestCase):
    def setUp(self):
        self.dependencies = {}

    def _new_conf(self, settings):
        with patch('xivo_dao.asterisk_conf_dao.find_features_settings'):
            conf = FeaturesConfGenerator(self.dependencies)
            conf._settings = settings
            return conf

    def test_minimal_settings(self):
        settings = {
            'general_options': [],
            'featuremap_options': [],
            'applicationmap_options': [],
        }

        features_conf_gen = self._new_conf(settings)
        features_conf = features_conf_gen.generate()

        assert_config_equal(
            features_conf,
            '''
            [general]

            [featuremap]

            [applicationmap]
        ''',
        )

    def test_settings(self):
        settings = {
            'general_options': [('pickupexten', '*8')],
            'featuremap_options': [('blindxfer', '*1')],
            'applicationmap_options': [('toto', '*1')],
        }

        features_conf_gen = self._new_conf(settings)

        features_conf = features_conf_gen.generate()

        assert_config_equal(
            features_conf,
            '''
            [general]
            pickupexten = *8

            [featuremap]
            blindxfer = *1

            [applicationmap]
            toto = *1
        ''',
        )
