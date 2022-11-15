# -*- coding: utf-8 -*-
# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from wazo_confgend.generators.util import AsteriskFileWriter
from xivo_dao import asterisk_conf_dao
import logging
import io


logger = logging.getLogger(__name__)


class FeaturesConfGenerator:
    def __init__(self, dependencies):
        self._settings = asterisk_conf_dao.find_features_settings()

    def _generate_general(self, ast_file):
        ast_file.write_section('general')
        ast_file.write_options(self._settings['general_options'])

    def _generate_featuremap(self, ast_file):
        ast_file.write_section('featuremap')
        ast_file.write_options(self._settings['featuremap_options'])

    def _generate_applicationmap(self, ast_file):
        ast_file.write_section('applicationmap')
        ast_file.write_options(self._settings['applicationmap_options'])

    def generate(self):
        logger.debug("Generating config for features.conf")
        output = io.StringIO()
        ast_file = AsteriskFileWriter(output)
        self._generate_general(ast_file)
        logger.debug("Generated general section for features.conf")
        self._generate_featuremap(ast_file)
        logger.debug("Generated featuremap section for features.conf")
        self._generate_applicationmap(ast_file)
        logger.debug("Generated applicationmap section for features.conf")
        return output.getvalue()
