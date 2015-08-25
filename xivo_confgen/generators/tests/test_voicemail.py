# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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
import textwrap

from hamcrest import assert_that, equal_to

from mock import patch, Mock
from xivo_confgen.generators.tests.util import assert_generates_config
from xivo_confgen.generators.voicemail import VoicemailConf, VoicemailGenerator

from xivo_dao.resources.voicemail.model import Voicemail


class TestVoicemailGenerator(unittest.TestCase):

    def setUp(self):
        self.voicemail_list = Mock()
        self.generator = VoicemailGenerator(self.voicemail_list)

    def test_given_no_voicemails_when_generating_then_generates_nothing(self):
        self.voicemail_list.return_value = []

        output = self.generator.generate()

        assert_that(output, equal_to(''))

    def test_given_voicemail_with_minimal_parameters_when_generating_then_generates_one_entry(self):
        self.voicemail_list.return_value = [Voicemail(name='myvoicemail',
                                                      number='1000',
                                                      context='default',
                                                      options=[])]

        expected = textwrap.dedent(
            """\
            [default]
            1000 => ,myvoicemail,,,

            """)

        output = self.generator.generate()
        assert_that(output, equal_to(expected))

    def test_given_voicemail_with_all_parameters_when_generating_then_generates_one_entry(self):
        self.voicemail_list.return_value = [Voicemail(name='myvoicemail',
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
                                                      ])]

        expected = textwrap.dedent(
            """\
            [default]
            1000 => 1234,myvoicemail,email@example.com,pager@example.com,language=fr_FR|tz=eu-fr|attach=yes|deletevoicemail=yes|maxmsg=5|volgain=0.5|saycid=yes

            """)

        output = self.generator.generate()
        assert_that(output, equal_to(expected))

    def test_given_voicemail_parameter_with_special_characters_when_generating_then_escapes_characters(self):
        self.voicemail_list.return_value = [Voicemail(name='myvoicemail',
                                                      number='1000',
                                                      context='default',
                                                      options=[
                                                          ["emailbody", "howdy\thello\nworld\r|!"],
                                                      ])]

        expected = textwrap.dedent(
            """\
            [default]
            1000 => ,myvoicemail,,,emailbody=howdy\\thello\\nworld\\r!

            """)

        output = self.generator.generate()
        assert_that(output, equal_to(expected))

    def test_given_two_voicemails_in_same_context_when_generating_then_generates_two_entries(self):
        self.voicemail_list.return_value = [Voicemail(name='myvoicemail',
                                                      number='1000',
                                                      context='default',
                                                      options=[]),
                                            Voicemail(name='othervoicemail',
                                                      number='1001',
                                                      context='default',
                                                      options=[])]

        expected = textwrap.dedent(
            """\
            [default]
            1000 => ,myvoicemail,,,
            1001 => ,othervoicemail,,,

            """)

        output = self.generator.generate()
        assert_that(output, equal_to(expected))

    def test_given_two_voicemails_in_different_contexts_when_generating_then_generates_two_contexts(self):
        self.voicemail_list.return_value = [Voicemail(name='myvoicemail',
                                                      number='1000',
                                                      context='default',
                                                      options=[]),
                                            Voicemail(name='othervoicemail',
                                                      number='1001',
                                                      context='otherctx',
                                                      options=[])]

        expected = textwrap.dedent(
            """\
            [default]
            1000 => ,myvoicemail,,,

            [otherctx]
            1001 => ,othervoicemail,,,

            """)

        output = self.generator.generate()
        assert_that(output, equal_to(expected))


class TestVoicemailConf(unittest.TestCase):

    @patch('xivo_dao.asterisk_conf_dao.find_voicemail_general_settings', Mock(return_value=[]))
    def setUp(self):
        self.voicemail_generator = Mock(VoicemailGenerator)
        self.voicemail_generator.generate.return_value = ''

        self.voicemail_conf = VoicemailConf(self.voicemail_generator)
        self.voicemail_conf._voicemail_settings = []

    def test_empty_sections(self):
        assert_generates_config(self.voicemail_conf, '''
            [general]

            [zonemessages]
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
