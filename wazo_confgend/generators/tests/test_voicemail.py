# -*- coding: utf-8 -*-
# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import textwrap

from hamcrest import assert_that, equal_to

from mock import patch, Mock
from wazo_confgend.generators.tests.util import assert_generates_config
from wazo_confgend.generators.voicemail import VoicemailConf, VoicemailGenerator

from xivo_dao.alchemy.voicemail import Voicemail


class TestVoicemailGenerator(unittest.TestCase):

    def test_given_no_voicemails_when_generating_then_generates_nothing(self):
        generator = VoicemailGenerator([])

        output = generator.generate()

        assert_that(output, equal_to(''))

    def test_given_voicemail_with_minimal_parameters_when_generating_then_generates_one_entry(self):
        generator = VoicemailGenerator([
            Voicemail(name='myvoicemail',
                      number='1000',
                      context='default',
                      options=[]),
        ])

        expected = textwrap.dedent(
            """\
            [default]
            1000 => ,myvoicemail,,,deletevoicemail=no

            """)

        output = generator.generate()
        assert_that(output, equal_to(expected))

    def test_given_voicemail_with_all_parameters_when_generating_then_generates_one_entry(self):
        generator = VoicemailGenerator([
            Voicemail(name='myvoicemail',
                      number='1000',
                      context='default',
                      password='1234',
                      email='email@example.com',
                      pager='pager@example.com',
                      language='fr_FR',
                      timezone='eu-fr',
                      attach_audio=True,
                      delete_messages=True,
                      max_messages=5,
                      ask_password=True,
                      options=[
                          ["volgain", "0.5"],
                          ["saycid", "yes"]
                      ]),
        ])

        expected = textwrap.dedent(
            """\
            [default]
            1000 => 1234,myvoicemail,email@example.com,pager@example.com,language=fr_FR|tz=eu-fr|attach=yes|deletevoicemail=yes|maxmsg=5|volgain=0.5|saycid=yes

            """)

        output = generator.generate()
        assert_that(output, equal_to(expected))

    def test_given_voicemail_parameter_with_special_characters_when_generating_then_escapes_characters(self):
        generator = VoicemailGenerator([
            Voicemail(name='myvoicemail',
                      number='1000',
                      context='default',
                      options=[
                          ["emailbody", "howdy\thello\nworld\r|!"],
                      ]),
        ])

        expected = textwrap.dedent(
            """\
            [default]
            1000 => ,myvoicemail,,,deletevoicemail=no|emailbody=howdy\\thello\\nworld\\r!

            """)

        output = generator.generate()
        assert_that(output, equal_to(expected))

    def test_given_two_voicemails_in_same_context_when_generating_then_generates_two_entries(self):
        generator = VoicemailGenerator([
            Voicemail(name='myvoicemail',
                      number='1000',
                      context='default',
                      options=[]),
            Voicemail(name='othervoicemail',
                      number='1001',
                      context='default',
                      options=[]),
        ])

        expected = textwrap.dedent(
            """\
            [default]
            1000 => ,myvoicemail,,,deletevoicemail=no
            1001 => ,othervoicemail,,,deletevoicemail=no

            """)

        output = generator.generate()
        assert_that(output, equal_to(expected))

    def test_given_two_voicemails_in_different_contexts_when_generating_then_generates_two_contexts(self):
        generator = VoicemailGenerator([
            Voicemail(name='myvoicemail',
                      number='1000',
                      context='default',
                      options=[]),
            Voicemail(name='othervoicemail',
                      number='1001',
                      context='otherctx',
                      options=[]),
        ])

        expected = textwrap.dedent(
            """\
            [default]
            1000 => ,myvoicemail,,,deletevoicemail=no

            [otherctx]
            1001 => ,othervoicemail,,,deletevoicemail=no

            """)

        output = generator.generate()
        assert_that(output, equal_to(expected))


class TestVoicemailConf(unittest.TestCase):

    @patch('xivo_dao.asterisk_conf_dao.find_voicemail_general_settings', Mock(return_value=[]))
    def setUp(self):
        self.voicemail_generator = Mock(VoicemailGenerator)
        self.voicemail_generator.generate.return_value = u''

        self.voicemail_conf = VoicemailConf(self.voicemail_generator)
        self.voicemail_conf._voicemail_settings = []

    def test_empty_sections(self):
        assert_generates_config(self.voicemail_conf, '''
            [general]

            [zonemessages]
        ''')

    @patch('xivo_dao.asterisk_conf_dao.find_voicemail_general_settings', Mock(return_value=[]))
    def test_non_ascii_voicemail(self):
        voicemail_generator = Mock(VoicemailGenerator)
        voicemail_generator.generate.return_value = u'[defaulté]'
        voicemail_conf = VoicemailConf(voicemail_generator)
        voicemail_conf._voicemail_settings = []

        assert_generates_config(voicemail_conf, u'''
            [general]

            [zonemessages]

            [defaulté]
        ''')

    def test_one_element_general_section(self):
        self.voicemail_conf._voicemail_settings = [{'category': u'general',
                                                    'var_name': u'foo',
                                                    'var_val': u'bar'}]

        assert_generates_config(self.voicemail_conf, '''
            [general]
            foo = bar

            [zonemessages]
        ''')

    def test_one_element_zonemessages_section(self):
        self.voicemail_conf._voicemail_settings = [{'category': u'zonemessages',
                                                    'var_name': u'foo',
                                                    'var_val': u'bar'}]

        assert_generates_config(self.voicemail_conf, '''
            [general]

            [zonemessages]
            foo = bar
        ''')

    def test_escape_general_emailbody_option(self):
        self.voicemail_conf._voicemail_settings = [{'category': u'general',
                                                    'var_name': u'emailbody',
                                                    'var_val': u'foo\nbar'}]

        assert_generates_config(self.voicemail_conf, '''
            [general]
            emailbody = foo\\nbar

            [zonemessages]
        ''')

    def test_voicemail_generation_included_in_config(self):
        self.voicemail_generator.generate.return_value = textwrap.dedent(
            """\
            [default]
            1000 => ,myvoicemail,,,

            """)

        assert_generates_config(self.voicemail_conf, '''
            [general]

            [zonemessages]

            [default]
            1000 => ,myvoicemail,,,
        ''')
