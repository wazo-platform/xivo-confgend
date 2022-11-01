# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import io

from hamcrest import assert_that, equal_to
from wazo_confgend.generators.util import AsteriskFileWriter


class TestAsteriskFileWriter(unittest.TestCase):

    def setUp(self):
        self.output = io.StringIO()
        self.ast_file = AsteriskFileWriter(self.output)

    def test_write_section(self):
        self.ast_file.write_section('foobar')

        assert_that(self.output.getvalue(), equal_to('[foobar]\n'))

    def test_write_section_tpl(self):
        self.ast_file.write_section_tpl('foobar')

        assert_that(self.output.getvalue(), equal_to('[foobar](!)\n'))

    def test_write_section_using_tpl(self):
        self.ast_file.write_section_using_tpl('foobar', 'base')

        assert_that(self.output.getvalue(), equal_to('[foobar](base)\n'))

    def test_write_option(self):
        self.ast_file.write_option('foo', 'bar')

        assert_that(self.output.getvalue(), equal_to('foo = bar\n'))

    def test_write_options(self):
        self.ast_file.write_options([('foo', 'bar'), ('pow', 'bang')])

        assert_that(self.output.getvalue(), equal_to('foo = bar\npow = bang\n'))

    def test_write_object_option(self):
        self.ast_file.write_object_option('foo', 'bar')

        assert_that(self.output.getvalue(), equal_to('foo => bar\n'))
