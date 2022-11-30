# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import logging
import configparser
import collections
import itertools


from wazo_confgend.generators.util import AsteriskFileWriter

logger = logging.getLogger(__name__)


class AsteriskFileGenerator:
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


class CustomConfigParserStorage(collections.UserDict):
    """configparser storage class customized for asterisk format parsing"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = collections.OrderedDict(self.data)
        self.counter = itertools.count(start=1)

    def __setitem__(self, k, v):
        if isinstance(v, list):
            # if list, we assume this is a new option declaration
            # configparser creates option values as list to deal with multiline values
            self.data[f"{next(self.counter)}:{k}"] = v
        else:
            # this is either a SectionProxy object,
            # or an option value transformed from list form to string(so not a new option)
            self.data[k] = v


class AsteriskConfigParser(configparser.RawConfigParser):
    def items(self, *args, **kwargs):
        # Coupled with above CustomConfigParserStorage class as dict_type,
        # we trick configparser into tracking each duplicate option declarations by storing them under different keys
        # This reverts the trick in order to expose duplicate options under their real name
        return [
            (option.split(":", maxsplit=1)[-1], value)
            for option, value in super().items(*args, **kwargs)
        ]


def asterisk_parser(food=None) -> AsteriskConfigParser:
    parser = AsteriskConfigParser(
        dict_type=CustomConfigParserStorage,
        strict=False,
        interpolation=None,
        empty_lines_in_values=False,
        inline_comment_prefixes=[";"],
    )
    if food:
        parser.read_file(food)
    return parser
