# -*- coding: utf-8 -*-
# Copyright 2014-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest

from mock import Mock
from hamcrest import assert_that, contains_exactly, contains_inanyorder, has_item

from wazo_confgend.hints.adaptor import (
    AgentAdaptor,
    BSFilterAdaptor,
    ConferenceAdaptor,
    CustomAdaptor,
    ForwardAdaptor,
    GroupMemberAdaptor,
    ServiceAdaptor,
    UserAdaptor,
    UserSharedHintAdaptor,
)

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


class TestUserSharedHintsAdaptor(TestAdaptor):

    def setUp(self):
        super(TestUserSharedHintsAdaptor, self).setUp()
        self.dao = Mock()
        hints = [
            Hint(extension='83f38716-27d8-45c5-8fa6-5c7cb18acb26', argument='PJSIP/abc&SCCP/1001'),
            Hint(extension='0486beeb-4e3d-415b-b32d-660f44f6bab8', argument='PJSIP/def&SCCP/1002'),
        ]
        self.dao.user_shared_hints.return_value = hints
        self.adaptor = UserSharedHintAdaptor(self.dao)

    def test_adaptor_generate_shared_user_hints(self):
        assert_that(self.adaptor.generate(), contains_inanyorder(
            contains_exactly('83f38716-27d8-45c5-8fa6-5c7cb18acb26', 'PJSIP/abc&SCCP/1001'),
            contains_exactly('0486beeb-4e3d-415b-b32d-660f44f6bab8', 'PJSIP/def&SCCP/1002'),
        ))


class TestConferenceAdaptor(TestAdaptor):

    def test_adaptor_generates_conference_hint(self):
        dao = Mock()
        dao.conference_hints.return_value = [Hint(conference_id=1, extension='4000')]

        adaptor = ConferenceAdaptor(dao)

        assert_that(adaptor.generate(CONTEXT), contains_exactly(('4000', 'confbridge:1')))
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
                    contains_exactly(('*73542***223*1234', 'Custom:*73542***223*1234')))
        self.dao.forward_hints.assert_called_once_with(CONTEXT)

    def test_given_hint_without_argument_then_generates_progfunckey_without_argument(self):
        self.dao.forward_hints.return_value = [Hint(user_id=42,
                                               extension='*23',
                                               argument=None)]

        assert_that(self.adaptor.generate(CONTEXT),
                    contains_exactly(('*73542***223', 'Custom:*73542***223')))


class TestServiceAdaptor(TestAdaptor):

    def test_adaptor_generates_service_hint(self):
        dao = Mock()
        dao.progfunckey_extension.return_value = '*735'
        dao.service_hints.return_value = [Hint(user_id=42,
                                               extension='*26',
                                               argument=None)]

        adaptor = ServiceAdaptor(dao)

        assert_that(adaptor.generate(CONTEXT),
                    contains_exactly(('*73542***226', 'Custom:*73542***226')))
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
                    contains_exactly(('*73542***231***356', 'Custom:*73542***231***356')))
        dao.agent_hints.assert_called_once_with(CONTEXT)


class TestCustomAdaptor(TestAdaptor):

    def test_adaptor_generates_custom_hint(self):
        dao = Mock()
        dao.custom_hints.return_value = [Hint(user_id=None,
                                              extension='1234',
                                              argument=None)]

        adaptor = CustomAdaptor(dao)

        assert_that(adaptor.generate(CONTEXT),
                    contains_exactly(('1234', 'Custom:1234')))
        dao.custom_hints.assert_called_once_with(CONTEXT)

    def test_that_non_ascii_characters_are_ignored(self):
        dao = Mock()
        dao.custom_hints.return_value = [
            Hint(user_id=None, extension=u'\xe9', argument=None),
        ]

        adaptor = CustomAdaptor(dao)

        try:
            list(adaptor.generate(CONTEXT))
        except Exception:
            raise AssertionError('Should not raise')

        dao.custom_hints.assert_called_once_with(CONTEXT)


class TestBSFilterAdaptor(TestAdaptor):

    def test_adaptor_generates_bsfilter_hint(self):
        dao = Mock()
        dao.bsfilter_hints.return_value = [Hint(user_id=42,
                                                extension='*37',
                                                argument='12')]

        adaptor = BSFilterAdaptor(dao)

        assert_that(adaptor.generate(CONTEXT),
                    contains_exactly(('*3712', 'Custom:*3712')))
        dao.bsfilter_hints.assert_called_once_with(CONTEXT)


class TestGroupMemberAdaptor(TestAdaptor):

    def test_adaptor_generates_groupmember_hint(self):
        dao = Mock()
        dao.progfunckey_extension.return_value = '*735'
        dao.groupmember_hints.return_value = [Hint(user_id=42,
                                                   extension='*50',
                                                   argument='18')]

        adaptor = GroupMemberAdaptor(dao)

        assert_that(adaptor.generate(CONTEXT),
                    contains_exactly(('*73542***250*18', 'Custom:*73542***250*18')))
        dao.groupmember_hints.assert_called_once_with(CONTEXT)
