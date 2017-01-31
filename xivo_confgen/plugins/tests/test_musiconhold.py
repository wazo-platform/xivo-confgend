# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

import unittest

from mock import Mock, patch
from jinja2.loaders import PackageLoader
from xivo_dao.alchemy.moh import MOH

from xivo_confgen.generators.tests.util import assert_config_equal
from xivo_confgen.template import TemplateHelper
from ..musiconhold_conf import MOHConfGenerator


class TestConfBridgeConf(unittest.TestCase):

    def setUp(self):
        self.moh_dao = Mock()
        loader = PackageLoader('xivo_confgen.template', 'templates')
        tpl_helper = TemplateHelper(loader)
        dependencies = {'tpl_helper': tpl_helper}
        self.generator = MOHConfGenerator(dependencies)

    @patch('xivo_confgen.plugins.musiconhold_conf.moh_dao')
    def test_generate_mode_files(self, mock_moh_dao):
        moh_list = [
            MOH(name='foo', mode='files', sort='alphabetical'),
        ]
        mock_moh_dao.find_all_by.return_value = moh_list

        value = self.generator.generate()

        assert_config_equal(value, '''
            [foo]
            mode = files
            directory = /var/lib/asterisk/moh/foo
            sort = alpha
        ''')

    @patch('xivo_confgen.plugins.musiconhold_conf.moh_dao')
    def test_generate_mode_custom(self, mock_moh_dao):
        moh_list = [
            MOH(name='bar', mode='custom', application='/bin/false rrr'),
        ]
        mock_moh_dao.find_all_by.return_value = moh_list

        value = self.generator.generate()

        assert_config_equal(value, '''
            [bar]
            mode = custom
            application = /bin/false rrr
        ''')

    @patch('xivo_confgen.plugins.musiconhold_conf.moh_dao')
    def test_generate_unknown_sort(self, mock_moh_dao):
        moh_list = [
            MOH(name='foo', mode='files', sort='rabbit'),
        ]
        mock_moh_dao.find_all_by.return_value = moh_list

        value = self.generator.generate()

        assert_config_equal(value, '''
            [foo]
            mode = files
            directory = /var/lib/asterisk/moh/foo
            sort = rabbit
        ''')
