# -*- coding: utf-8 -*-

# Copyright (C) 2011-2015 Avencall
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

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import all_of
from hamcrest import starts_with
from hamcrest import ends_with
from hamcrest import equal_to_ignoring_whitespace
from hamcrest import contains_inanyorder


def assert_generates_config(generator, expected):
    output = StringIO.StringIO()
    generator.generate(output)

    assert_config_equal(output.getvalue(), expected)


def assert_config_equal(config, expected):
    actual_lines = clean_lines(config)
    expected_lines = clean_lines(expected)

    assert_that('\n'.join(actual_lines), equal_to('\n'.join(expected_lines)))


def assert_section_equal(config, expected):
    config = clean_lines(config)
    expected = clean_lines(expected)
    # check section name is the same in the first line
    assert_that(config[0], all_of(starts_with('['), ends_with(']')))
    assert_that(config[0], equal_to_ignoring_whitespace(expected[0]))

    # check section content
    expected_matchers = [equal_to_ignoring_whitespace(line) for line in expected[1:]]
    assert_that(config[1:], contains_inanyorder(*expected_matchers))


def clean_lines(lines):
    result = []
    for line in lines.split('\n'):
        line = line.lstrip()
        if line:
            result.append(line)
    return result
