# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confgen.generators.util import AsteriskFileWriter
from xivo_dao import asterisk_conf_dao


class FeaturesConf(object):

    def __init__(self):
        self._settings = asterisk_conf_dao.find_features_settings()

    def generate(self, output):
        ast_file = AsteriskFileWriter(output)
        self._generate_general(ast_file)
        self._generate_featuremap(ast_file)
        self._generate_applicationmap(ast_file)

    def _generate_general(self, ast_file):
        ast_file.write_section(u'general')
        ast_file.write_options(self._settings['general_options'])

    def _generate_featuremap(self, ast_file):
        ast_file.write_section(u'featuremap')
        ast_file.write_options(self._settings['featuremap_options'])

    def _generate_applicationmap(self, ast_file):
        ast_file.write_section(u'applicationmap')
        ast_file.write_options(self._settings['applicationmap_options'])
