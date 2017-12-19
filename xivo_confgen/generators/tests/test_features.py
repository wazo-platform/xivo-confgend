# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import patch
from xivo_confgen.generators.features import FeaturesConf
from xivo_confgen.generators.tests.util import assert_generates_config


class TestFeaturesConf(unittest.TestCase):

    def _new_conf(self, settings):
        with patch('xivo_dao.asterisk_conf_dao.find_features_settings'):
            conf = FeaturesConf()
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
            'general_options': [(u'pickupexten', u'*8')],
            'featuremap_options': [(u'blindxfer', u'*1')],
            'applicationmap_options': [(u'toto', u'*1')],
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
