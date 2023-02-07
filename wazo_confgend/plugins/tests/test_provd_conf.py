# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import textwrap

from unittest.mock import Mock, patch
from wazo_confgend.generators.tests.util import assert_config_equal

from ..provd_conf import ProvdNetworkConfGenerator


class TestProvdNetworkConf(unittest.TestCase):
    def setUp(self):
        dependencies = {'config': {}}
        self.generator = ProvdNetworkConfGenerator(dependencies)

    @patch('wazo_confgend.plugins.provd_conf.session_scope')
    def test_net4_ip_in_provisioning(self, session_scope):
        session_scope.__enter__ = Mock(return_value=Mock())
        session_scope.__exit__ = Mock(return_value=None)

        with patch.object(
            self.generator, 'get_provd_net4_ip'
        ) as provd_net4_ip, patch.object(
            self.generator, 'get_provd_http_port'
        ) as provd_http_port, patch.object(
            self.generator, 'get_netiface_net4_ip'
        ) as netiface_net4_ip:
            provd_net4_ip.return_value = '10.0.0.254'
            provd_http_port.return_value = None
            netiface_net4_ip.return_value = None

            value = self.generator.generate()

        assert_config_equal(
            value,
            textwrap.dedent(
                '''\
            general:
                external_ip: 10.0.0.254
        '''
            ),
        )

    @patch('wazo_confgend.plugins.provd_conf.session_scope')
    def test_net4_ip_in_netiface(self, session_scope):
        session_scope.__enter__ = Mock(return_value=Mock())
        session_scope.__exit__ = Mock(return_value=None)

        with patch.object(
            self.generator, 'get_provd_net4_ip'
        ) as provd_net4_ip, patch.object(
            self.generator, 'get_netiface_net4_ip'
        ) as netiface_net4_ip, patch.object(
            self.generator, 'get_provd_http_port'
        ) as provd_http_port:
            provd_net4_ip.return_value = None
            provd_http_port.return_value = None
            netiface_net4_ip.return_value = '10.0.0.250'

            value = self.generator.generate()

        assert_config_equal(
            value,
            textwrap.dedent(
                '''\
            general:
                external_ip: 10.0.0.250
        '''
            ),
        )

    @patch('wazo_confgend.plugins.provd_conf.session_scope')
    def test_complete_configuration(self, session_scope):
        session_scope.__enter__ = Mock(return_value=Mock())
        session_scope.__exit__ = Mock(return_value=None)

        with patch.object(
            self.generator, 'get_provd_net4_ip'
        ) as provd_net4_ip, patch.object(
            self.generator, 'get_netiface_net4_ip'
        ) as netiface_net4_ip, patch.object(
            self.generator, 'get_provd_http_port'
        ) as provd_http_port:
            provd_net4_ip.return_value = '10.0.0.254'
            provd_http_port.return_value = 8666
            netiface_net4_ip.return_value = '10.0.0.222'

            value = self.generator.generate()

        assert_config_equal(
            value,
            textwrap.dedent(
                '''\
            general:
                external_ip: 10.0.0.254
                http_port: 8666
        '''
            ),
        )

    @patch('wazo_confgend.plugins.provd_conf.session_scope')
    def test_no_external_ip(self, session_scope):
        session_scope.__enter__ = Mock(return_value=Mock())
        session_scope.__exit__ = Mock(return_value=None)

        with patch.object(
            self.generator, 'get_provd_net4_ip'
        ) as provd_net4_ip, patch.object(
            self.generator, 'get_provd_http_port'
        ) as provd_http_port, patch.object(
            self.generator, 'get_netiface_net4_ip'
        ) as netiface_net4_ip:
            provd_net4_ip.return_value = None
            provd_http_port.return_value = None
            netiface_net4_ip.return_value = None

            value = self.generator.generate()

        assert_config_equal(value, '{}')
