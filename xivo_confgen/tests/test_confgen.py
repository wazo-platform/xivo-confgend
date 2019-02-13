# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import tempfile

from hamcrest import (
    assert_that,
    equal_to,
)
from mock import Mock

from ..confgen import (
    Confgen,
    ConfgendFactory,
)


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

    def test_receive_with_arguments(self):
        cmd = 'resource/filename.conf  arg1    arg2\n'

        self.protocol.dataReceived(cmd)

        self.factory.generate.assert_called_once_with('resource', 'filename.conf', 'arg1', 'arg2')
        self.transport.write.assert_called_once_with(self.factory.generate.return_value)


class TestConfgendFactory(unittest.TestCase):

    def setUp(self):
        config = {
            'templates': {'contextsconf': ''},
            'plugins': {},
        }
        cachedir = tempfile.gettempdir()

        self.factory = ConfgendFactory(cachedir, config)
        self.factory._handler_factory = self.handler_factory = Mock()
        self.handler = self.handler_factory.get.return_value
        self.get_cached_content = self.factory._get_cached_content = Mock()
        self.cache = self.factory._cache = Mock()

    def test_generate_from_handler(self):
        self.handler.return_value = 'some content'

        result = self.factory.generate('test', 'myfile.yml')

        assert_that(result, equal_to(self.handler.return_value))

    def test_that_error_on_generate_returns_cached_value(self):
        self.handler.side_effect = Exception
        self.get_cached_content.return_value = 'cached content'

        result = self.factory.generate('test', 'myfile.yml')

        assert_that(result, equal_to(self.get_cached_content.return_value))

    def test_that_the_cached_argument_returns_the_cached_value(self):
        self.handler.return_value = 'some content'
        self.get_cached_content.return_value = 'cached content'

        result = self.factory.generate('test', 'myfile.yml', 'cached')

        assert_that(result, equal_to(self.get_cached_content.return_value))

    def test_that_the_cached_argument_returns_the_a_generated_value_when_no_cache(self):
        self.handler.return_value = 'some content'
        self.get_cached_content.return_value = None

        result = self.factory.generate('test', 'myfile.yml', 'cached')

        assert_that(result, equal_to(self.handler.return_value))

    def test_the_invalidate_command(self):
        result = self.factory.generate('test', 'myfile.yml', 'invalidate')

        assert_that(result, equal_to(None))
        self.cache.invalidate.assert_called_once_with('test/myfile.yml')
