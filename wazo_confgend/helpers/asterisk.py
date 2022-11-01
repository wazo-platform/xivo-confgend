# -*- coding: utf-8 -*-
# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later



import logging
from wazo_confgend.generators.util import AsteriskFileWriter

logger = logging.getLogger(__name__)


class AsteriskFileGenerator(object):

    def __init__(self, dao):
        self.asterisk_file_dao = dao

    def generate(self, name, output, required_sections=None):
        file_ = self.asterisk_file_dao.find_by(name=name)
        self._generate_file(file_, output, required_sections)

    def _generate_file(self, file_, output, required_sections=None):
        section_names = set()
        writer = AsteriskFileWriter(output)

        if not file_:
            self._generate_missing_sections(writer, section_names, required_sections)
            return

        for section in file_.sections_ordered:
            writer.write_section(section.name)
            section_names.add(section.name)
            for variable in section.variables:
                writer.write_option(variable.key, variable.value or '')

        self._generate_missing_sections(writer, section_names, required_sections)
        writer._write_section_separator()

    def _generate_missing_sections(self, writer, sections, required_sections):
        for required_section in required_sections or []:
            if required_section in sections:
                continue
            logger.info(
                'generated an empty section "%s" which was missing from the DB',
                required_section,
            )
            writer.write_section(required_section)
            writer._write_section_separator()
            sections.add(required_section)
