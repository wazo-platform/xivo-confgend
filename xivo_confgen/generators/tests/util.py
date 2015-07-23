# -*- coding: utf-8 -*-

# Copyright (C) 2011-2014 Avencall
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

import StringIO

from hamcrest import assert_that, equal_to


def assert_generates_config(generator, expected):
    output = StringIO.StringIO()
    generator.generate(output)

    assert_config_equal(output.getvalue(), expected)


def assert_config_equal(config, expected):
    actual_lines = []
    for line in config.split('\n'):
        if line:
            actual_lines.append(line)

    expected_lines = []
    for line in expected.split('\n'):
        line = line.lstrip()
        if line:
            expected_lines.append(line)

    assert_that('\n'.join(actual_lines), equal_to('\n'.join(expected_lines)))
