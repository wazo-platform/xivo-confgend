# -*- coding: utf-8 -*-
# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from os.path import basename
from unittest import TestCase

from jinja2 import PackageLoader, Template
from hamcrest import assert_that, contains_string, equal_to

from ..template import TemplateHelper


class TestTemplateHelper(TestCase):

    def setUp(self):
        self.loader = PackageLoader('wazo_confgend', 'tests/templates')
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


class TestIVRTemplate(TestCase):

    def setUp(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        self.template_path = os.path.abspath(
            os.path.join(
                cwd, '..', 'templates', 'asterisk', 'extensions', 'ivr.jinja',
            ),
        )

    def test_ivr_escaping_choices_destinations(self):
        with open(self.template_path) as f:
            template = Template(f.read())

        ivr = {
            'id': 42,
            'choices': [
                {
                    'destination': {'gosub_args': 'queue,1,5.0;2;'},
                    'exten': '1',
                }
            ],
        }

        output = template.render(ivr=ivr)

        assert_that(
            output,
            contains_string(r'Gosub(forward,s,1(queue,1,5.0\;2\;'),
        )

    def test_ivr_escaping_timeout_destination(self):
        with open(self.template_path) as f:
            template = Template(f.read())

        ivr = {
            'id': 42,
            'timeout_destination': {'gosub_args': 'queue,1,5.0;2;'},
        }

        output = template.render(ivr=ivr)

        assert_that(
            output,
            contains_string(r'Gosub(forward,s,1(queue,1,5.0\;2\;'),
        )

    def test_ivr_escaping_invalid_destination(self):
        with open(self.template_path) as f:
            template = Template(f.read())

        ivr = {
            'id': 42,
            'invalid_destination': {'gosub_args': 'queue,1,5.0;2;'},
        }

        output = template.render(ivr=ivr)

        assert_that(
            output,
            contains_string(r'Gosub(forward,s,1(queue,1,5.0\;2\;'),
        )

    def test_ivr_escaping_abort_destination(self):
        with open(self.template_path) as f:
            template = Template(f.read())

        ivr = {
            'id': 42,
            'abort_destination': {'gosub_args': 'queue,1,5.0;2;'},
        }

        output = template.render(ivr=ivr)

        assert_that(
            output,
            contains_string(r'Gosub(forward,s,1(queue,1,5.0\;2\;'),
        )
