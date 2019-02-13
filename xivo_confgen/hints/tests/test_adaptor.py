# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest

from mock import Mock
from hamcrest import assert_that, contains, has_item

from xivo_confgen.hints.adaptor import UserAdaptor
from xivo_confgen.hints.adaptor import ConferenceAdaptor
from xivo_confgen.hints.adaptor import ForwardAdaptor
from xivo_confgen.hints.adaptor import ServiceAdaptor
from xivo_confgen.hints.adaptor import AgentAdaptor
from xivo_confgen.hints.adaptor import CustomAdaptor
from xivo_confgen.hints.adaptor import BSFilterAdaptor

from xivo_dao.resources.func_key.model import Hint

CONTEXT = 'context'


class TestAdaptor(unittest.TestCase):
    pass


class TestUserAdaptor(TestAdaptor):

    def setUp(self):
        super(TestUserAdaptor, self).setUp()
        self.dao = Mock()
        self.dao.user_hints.return_value = [Hint(user_id=42,
                                                 extension='1000',
                                                 argument='SIP/abcdef')]

        self.adaptor = UserAdaptor(self.dao)

    def test_adaptor_generates_user_hint(self):
        assert_that(self.adaptor.generate(CONTEXT), has_item(('1000', 'SIP/abcdef')))
        self.dao.user_hints.assert_called_once_with(CONTEXT)


class TestConferenceAdaptor(TestAdaptor):

    def test_adaptor_generates_conference_hint(self):
        dao = Mock()
        dao.conference_hints.return_value = [Hint(user_id=None,
                                                  extension='4000',
                                                  argument=None)]

        adaptor = ConferenceAdaptor(dao)

        assert_that(adaptor.generate(CONTEXT), contains(('4000', 'meetme:4000')))
        dao.conference_hints.assert_called_once_with(CONTEXT)


class TestForwardAdaptor(TestAdaptor):

    def setUp(self):
        super(TestForwardAdaptor, self).setUp()
        self.dao = Mock()
        self.dao.progfunckey_extension.return_value = '*735'

        self.adaptor = ForwardAdaptor(self.dao)

    def test_given_hint_with_argument_then_generates_progfunckey_with_argument(self):
        self.dao.forward_hints.return_value = [Hint(user_id=42,
                                               extension='*23',
                                               argument='1234')]

        assert_that(self.adaptor.generate(CONTEXT),
                    contains(('*73542***223*1234', 'Custom:*73542***223*1234')))
        self.dao.forward_hints.assert_called_once_with(CONTEXT)

    def test_given_hint_without_argument_then_generates_progfunckey_without_argument(self):
        self.dao.forward_hints.return_value = [Hint(user_id=42,
                                               extension='*23',
                                               argument=None)]

        assert_that(self.adaptor.generate(CONTEXT),
                    contains(('*73542***223', 'Custom:*73542***223')))


class TestServiceAdaptor(TestAdaptor):

    def test_adaptor_generates_service_hint(self):
        dao = Mock()
        dao.progfunckey_extension.return_value = '*735'
        dao.service_hints.return_value = [Hint(user_id=42,
                                               extension='*26',
                                               argument=None)]

        adaptor = ServiceAdaptor(dao)

        assert_that(adaptor.generate(CONTEXT),
                    contains(('*73542***226', 'Custom:*73542***226')))
        dao.service_hints.assert_called_once_with(CONTEXT)


class TestAgentAdaptor(TestAdaptor):

    def test_adaptor_generates_service_hint(self):
        dao = Mock()
        dao.progfunckey_extension.return_value = '*735'
        dao.agent_hints.return_value = [Hint(user_id=42,
                                             extension='*31',
                                             argument='56')]

        adaptor = AgentAdaptor(dao)

        assert_that(adaptor.generate(CONTEXT),
                    contains(('*73542***231***356', 'Custom:*73542***231***356')))
        dao.agent_hints.assert_called_once_with(CONTEXT)


class TestCustomAdaptor(TestAdaptor):

    def test_adaptor_generates_custom_hint(self):
        dao = Mock()
        dao.custom_hints.return_value = [Hint(user_id=None,
                                              extension='1234',
                                              argument=None)]

        adaptor = CustomAdaptor(dao)

        assert_that(adaptor.generate(CONTEXT),
                    contains(('1234', 'Custom:1234')))
        dao.custom_hints.assert_called_once_with(CONTEXT)


class TestBSFilterAdaptor(TestAdaptor):

    def test_adaptor_generates_bsfilter_hint(self):
        dao = Mock()
        dao.bsfilter_hints.return_value = [Hint(user_id=42,
                                                extension='*37',
                                                argument='12')]

        adaptor = BSFilterAdaptor(dao)

        assert_that(adaptor.generate(CONTEXT),
                    contains(('*3712', 'Custom:*3712')))
        dao.bsfilter_hints.assert_called_once_with(CONTEXT)
