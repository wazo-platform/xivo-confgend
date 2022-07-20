# -*- coding: utf-8 -*-
# Copyright 2011-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import sys

from mock import Mock

from wazo_confgend.asterisk import AsteriskFrontend


class Test(unittest.TestCase):

    def setUp(self):
        self._config = {
            'templates': {'contextsconf': None},
        }
        self.tpl_helper = Mock()
        self.asteriskFrontEnd = AsteriskFrontend(self._config, self.tpl_helper)

    def test_encoding(self):
        charset = ("ascii", "US-ASCII",)
        self.assertTrue(sys.getdefaultencoding() in charset, "Test should be run in ascii, in eclipse change run configuration common tab")
