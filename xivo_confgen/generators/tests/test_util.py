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
import StringIO

from hamcrest import assert_that, equal_to
from xivo_confgen.generators.util import AsteriskFileWriter


class TestAsteriskFileWriter(unittest.TestCase):

    def setUp(self):
        self.output = StringIO.StringIO()
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
