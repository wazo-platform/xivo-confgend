# -*- coding: utf-8 -*-
# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock, patch
from jinja2.loaders import PackageLoader
from xivo_dao.alchemy.moh import MOH

from wazo_confgend.generators.tests.util import assert_config_equal
from wazo_confgend.template import TemplateHelper
from ..musiconhold_conf import MOHConfGenerator


class TestConfBridgeConf(unittest.TestCase):
    def setUp(self):
        self.moh_dao = Mock()
        loader = PackageLoader('wazo_confgend.template', 'templates')
        tpl_helper = TemplateHelper(loader)
        dependencies = {'tpl_helper': tpl_helper}
        self.generator = MOHConfGenerator(dependencies)

    @patch('wazo_confgend.plugins.musiconhold_conf.moh_dao')
    def test_generate_mode_files(self, mock_moh_dao):
        moh_list = [
            MOH(name='foo', mode='files', sort='alphabetical'),
        ]
        mock_moh_dao.find_all_by.return_value = moh_list

        value = self.generator.generate()

        assert_config_equal(
            value,
            '''
            [foo]
            mode = files
            directory = /var/lib/asterisk/moh/foo
            sort = alpha
        ''',
        )

    @patch('wazo_confgend.plugins.musiconhold_conf.moh_dao')
    def test_generate_mode_custom(self, mock_moh_dao):
        moh_list = [
            MOH(name='bar', mode='custom', application='/bin/false rrr'),
        ]
        mock_moh_dao.find_all_by.return_value = moh_list

        value = self.generator.generate()

        assert_config_equal(
            value,
            '''
            [bar]
            mode = custom
            application = /bin/false rrr
        ''',
        )

    @patch('wazo_confgend.plugins.musiconhold_conf.moh_dao')
    def test_generate_unknown_sort(self, mock_moh_dao):
        moh_list = [
            MOH(name='foo', mode='files', sort='rabbit'),
        ]
        mock_moh_dao.find_all_by.return_value = moh_list

        value = self.generator.generate()

        assert_config_equal(
            value,
            '''
            [foo]
            mode = files
            directory = /var/lib/asterisk/moh/foo
            sort = rabbit
        ''',
        )
