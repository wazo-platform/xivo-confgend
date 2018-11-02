# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import (
    assert_that,
    equal_to,
)

from ..pjsip_conf import AsteriskConfFileGenerator


class TestConfFileGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = AsteriskConfFileGenerator()

    def test_generate(self):
        data = [
            # section, type, templates, fields
            ('global', 'section', None, [('type', 'global'), ('user_agent', 'Wazo')]),
            ('global', 'extends', None, [('debug', 'yes')]),
            ('general-abc', 'template', None, [('disallow', 'all'), ('allow', 'ulaw')]),
            ('webrtc-endpoint', 'template', ['a', 'b'], [('transport', 'transport-wss')]),
            ('peer1', 'section', ['general-abc'], [('type', 'endpoint')]),
            ('peer1', 'extends', ['webrtc-endpoint'], [('context', 'inside')]),
        ]

        result = self.generator.generate(data)

        expected = '''\
[global]
type = global
user_agent = Wazo

[global](+)
debug = yes

[general-abc](!)
disallow = all
allow = ulaw

[webrtc-endpoint](!,a,b)
transport = transport-wss

[peer1](general-abc)
type = endpoint

[peer1](+,webrtc-endpoint)
context = inside
'''

        assert_that(result, equal_to(expected))
