# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from StringIO import StringIO
from os.path import basename
from unittest import TestCase

from jinja2 import PackageLoader
from hamcrest import assert_that, contains_string, equal_to

from ..template import TemplateHelper


class TestTemplateHelper(TestCase):

    def setUp(self):
        self.loader = PackageLoader(__name__, 'templates')
        self.tpl_helper = TemplateHelper(self.loader)

    def test_get_template(self):
        template = self.tpl_helper.get_template('foo')

        assert_that(basename(template._jinja_template.filename), equal_to('foo.jinja'))

    def test_get_customizable_template(self):
        template = self.tpl_helper.get_customizable_template('foo', 'custom')

        assert_that(basename(template._jinja_template.filename), equal_to('foo-custom.jinja'))

    def test_get_customizable_template_no_custom(self):
        template = self.tpl_helper.get_customizable_template('foo', 'mrgbl')

        assert_that(basename(template._jinja_template.filename), equal_to('foo.jinja'))

    def test_dump_template(self):
        template = self.tpl_helper.get_template('foo')

        output = template.dump({'value': 'hello world'})

        assert_that(output, contains_string('hello world'))

    def test_generate_template(self):
        output = StringIO()
        template = self.tpl_helper.get_template('foo')

        template.generate({'value': 'hello world'}, output)

        assert_that(output.getvalue(), contains_string('hello world'))
