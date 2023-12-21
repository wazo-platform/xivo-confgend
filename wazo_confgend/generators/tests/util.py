# Copyright 2011-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import io

from hamcrest import (
    all_of,
    assert_that,
    contains_inanyorder,
    ends_with,
    equal_to,
    equal_to_ignoring_whitespace,
    has_items,
    starts_with,
)


def assert_generates_config(generator, expected):
    output = io.StringIO()
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
    return all_of(
        starts_with('['), ends_with(']'), equal_to_ignoring_whitespace(expected)
    )


def _section_body_matchers(expected):
    return [equal_to_ignoring_whitespace(line) for line in expected]


def _clean_lines(lines):
    result = []
    for line in lines.split('\n'):
        line = line.lstrip()
        if line:
            result.append(line)
    return result
