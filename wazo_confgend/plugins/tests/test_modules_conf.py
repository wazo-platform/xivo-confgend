# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import tempfile
import unittest

from wazo_confgend.generators.tests.util import assert_config_equal

from ..modules_conf import ModulesConfGenerator

TEMPLATE = b'''\
{% for module in modules -%}
{{ module }}
{% endfor -%}
'''


class TestModulesConfGenerator(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(
            suffix='.conf.jinja2', mode='wb', delete=False
        ) as f:
            self.template_filename = f.name
            f.write(TEMPLATE)

        dependencies = {
            'config': {
                'templates': {'modulesconf': self.template_filename},
                'enabled_asterisk_modules': {
                    'chan_sip.so': False,
                    'chan_dahdi.so': True,
                    'chan_skinny.so': False,
                },
            }
        }
        self.generator = ModulesConfGenerator(dependencies)

    def tearDown(self):
        os.unlink(self.template_filename)

    def test_generate(self):
        result = self.generator.generate()

        assert_config_equal(
            result,
            '''
            chan_sip.so
            chan_skinny.so
        ''',
        )
