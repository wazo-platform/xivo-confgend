# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from wazo_confgend.generators.util import AsteriskFileWriter


class AsteriskFileGenerator(object):

    def __init__(self, dao):
        self.asterisk_file_dao = dao

    def generate(self, name, output):
        file_ = self.asterisk_file_dao.find_by(name=name)
        self._generate_file(file_, output)

    def _generate_file(self, file_, output):
        if not file_:
            return

        writer = AsteriskFileWriter(output)
        for section in file_.sections_ordered:
            writer.write_section(section.name)
            for variable in section.variables:
                writer.write_option(variable.key, variable.value or '')
        writer._write_section_separator()
