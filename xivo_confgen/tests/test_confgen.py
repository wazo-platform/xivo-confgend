# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from ..confgen import Confgen


class TestConfgen(unittest.TestCase):

    def setUp(self):
        self.factory = Mock()
        self.transport = Mock()
        self.protocol = Confgen()
        self.protocol.factory = self.factory
        self.protocol.transport = self.transport

    def test_receive_command(self):
        cmd = 'resource/filename.conf\n'

        self.protocol.dataReceived(cmd)

        self.factory.generate.assert_called_once_with('resource', 'filename.conf')
        self.transport.write.assert_called_once_with(self.factory.generate.return_value)

    def test_receive_command_no_result(self):
        self.factory.generate.return_value = None
        cmd = 'resource/filename.conf\n'

        self.protocol.dataReceived(cmd)

        self.factory.generate.assert_called_once_with('resource', 'filename.conf')
        self.transport.write.assert_not_called()
