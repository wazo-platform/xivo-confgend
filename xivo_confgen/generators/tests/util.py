# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016 Avencall
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

from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import contains_inanyorder
from hamcrest import ends_with
from hamcrest import equal_to
from hamcrest import equal_to_ignoring_whitespace
from hamcrest import has_items
from hamcrest import starts_with


def assert_generates_config(generator, expected):
    output = StringIO.StringIO()
    generator.generate(output)

    assert_config_equal(output.getvalue(), expected)


def assert_config_equal(config, expected):
    actual_lines = _clean_lines(config)
    expected_lines = _clean_lines(expected)

    assert_that('\n'.join(actual_lines), equal_to('\n'.join(expected_lines)))


def assert_section_equal(config, expected):
    config = _clean_lines(config)
    expected = _clean_lines(expected)
    assert_lines_equal(config, expected)


def assert_lines_equal(config, expected):
    assert_that(config[0], _equal_to_section_name(expected[0]))
    assert_that(config[1:], contains_inanyorder(*_section_body_matchers(expected[1:])))


def assert_lines_contain(config, expected):
    assert_that(config[0], _equal_to_section_name(expected[0]))
    assert_that(config[1:], has_items(*_section_body_matchers(expected[1:])))


def _equal_to_section_name(expected):
    return all_of(starts_with('['),
                  ends_with(']'),
                  equal_to_ignoring_whitespace(expected))


def _section_body_matchers(expected):
    return [equal_to_ignoring_whitespace(line) for line in expected]


def _clean_lines(lines):
    result = []
    for line in lines.split('\n'):
        line = line.lstrip()
        if line:
            result.append(line)
    return result
