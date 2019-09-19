# -*- coding: utf-8 -*-
# Copyright 2014-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock
from hamcrest import assert_that, contains

from wazo_confgend.hints.generator import HintGenerator
from wazo_confgend.hints.adaptor import HintAdaptor

CONTEXT = 'context'


class TestGenerator(unittest.TestCase):

    def test_given_an_adaptor_that_generates_nothing_then_generator_returns_an_empty_list(self):
        adaptor = Mock(HintAdaptor)
        adaptor.generate.return_value = []

        generator = HintGenerator([adaptor], [])

        assert_that(generator.generate(CONTEXT), contains())

    def test_given_an_adaptor_generates_a_hint_then_generator_returns_formatted_hint(self):
        adaptor = Mock(HintAdaptor)
        adaptor.generate.return_value = [('4000', 'Meetme:4000')]

        generator = HintGenerator([adaptor], [])

        assert_that(generator.generate(CONTEXT), contains('exten = 4000,hint,Meetme:4000'))
        adaptor.generate.assert_called_once_with(CONTEXT)

    def test_given_2_adaptors_then_generates_hint_for_all_adaptors(self):
        first_adaptor = Mock(HintAdaptor)
        first_adaptor.generate.return_value = [('1000', '1000')]

        second_adaptor = Mock(HintAdaptor)
        second_adaptor.generate.return_value = [('4000', 'Meetme:4000')]

        generator = HintGenerator([first_adaptor, second_adaptor], [])

        assert_that(generator.generate(CONTEXT),
                    contains('exten = 1000,hint,1000',
                             'exten = 4000,hint,Meetme:4000'))
        first_adaptor.generate.assert_called_once_with(CONTEXT)
        second_adaptor.generate.assert_called_once_with(CONTEXT)

    def test_given_2_adaptors_generate_same_hint_then_generator_returns_hint_only_once(self):
        first_adaptor = Mock(HintAdaptor)
        first_adaptor.generate.return_value = [('1000', 'SIP/abcdef')]

        second_adaptor = Mock(HintAdaptor)
        second_adaptor.generate.return_value = [('1000', 'Custom:1000')]

        generator = HintGenerator([first_adaptor, second_adaptor], [])

        assert_that(generator.generate(CONTEXT), contains('exten = 1000,hint,PJSIP/abcdef'))
        first_adaptor.generate.assert_called_once_with(CONTEXT)
        second_adaptor.generate.assert_called_once_with(CONTEXT)

    def test_that_global_adaptors_are_called(self):
        first_adaptor = Mock(HintAdaptor)
        first_adaptor.generate.return_value = [('1001', 'PJSIP/abc&SCCP/1042')]

        generator = HintGenerator([], [first_adaptor])

        assert_that(generator.generate_global_hints(), contains(
            'exten = 1001,hint,PJSIP/abc&SCCP/1042',
        ))
