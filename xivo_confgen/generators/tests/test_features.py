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
        }

        features_conf = self._new_conf(settings)

        assert_generates_config(features_conf, '''
            [general]

            [featuremap]
        ''')

    def test_settings(self):
        settings = {
            'general_options': [(u'pickupexten', u'*8')],
            'featuremap_options': [(u'blindxfer', u'*1')],
        }

        features_conf = self._new_conf(settings)

        assert_generates_config(features_conf, '''
            [general]
            pickupexten = *8

            [featuremap]
            blindxfer = *1
        ''')
