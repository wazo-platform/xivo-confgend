# Copyright 2011-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


def format_ast_comment(comment):
    return f'; {comment}'


def format_ast_section(name):
    return f'[{name}]'


def format_ast_section_tpl(name):
    return f'[{name}](!)'


def format_ast_section_using_tpl(name, tpl_name):
    return f'[{name}]({tpl_name})'


def format_ast_option(name, value):
    return f'{name} = {value}'.strip()


def format_ast_object_option(name, value):
    return f'{name} => {value}'.strip()


def format_none_as_empty(value):
    if value is None:
        return ''
    else:
        return value


class AsteriskFileWriter:
    def __init__(self, fobj):
        self._fobj = fobj
        self._first_section = True

    def write_section(self, name, comment=None):
        self._write_section_separator()
        if comment:
            self._write_line(format_ast_comment(comment))
        self._write_line(format_ast_section(name))

    def write_section_tpl(self, name):
        self._write_section_separator()
        self._write_line(format_ast_section_tpl(name))

    def write_section_using_tpl(self, name, tpl_name):
        self._write_section_separator()
        self._write_line(format_ast_section_using_tpl(name, tpl_name))

    def _write_section_separator(self):
        if self._first_section:
            self._first_section = False
        else:
            self._fobj.write('\n')

    def write_option(self, name, value):
        self._write_line(format_ast_option(name, value))

    def write_options(self, options):
        for name, value in options:
            self.write_option(name, value)

    def write_object_option(self, name, value):
        self._write_line(format_ast_object_option(name, value))

    def write_newline(self):
        self._fobj.write('\n')

    def _write_line(self, line):
        self._fobj.write(f'{line}\n')
