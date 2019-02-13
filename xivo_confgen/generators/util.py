# -*- coding: utf-8 -*-
# Copyright (C) 2011-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later


def format_ast_section(name):
    return u'[%s]' % name


def format_ast_section_tpl(name):
    return u'[%s](!)' % name


def format_ast_section_using_tpl(name, tpl_name):
    return u'[%s](%s)' % (name, tpl_name)


def format_ast_option(name, value):
    return u'%s = %s' % (name, value)


def format_ast_object_option(name, value):
    return u'%s => %s' % (name, value)


def format_none_as_empty(value):
    if value is None:
        return u''
    else:
        return value


class AsteriskFileWriter(object):

    def __init__(self, fobj):
        self._fobj = fobj
        self._first_section = True

    def write_section(self, name):
        self._write_section_separator()
        self._fobj.write(u'[{}]\n'.format(name))

    def write_section_tpl(self, name):
        self._write_section_separator()
        self._fobj.write(u'[{}](!)\n'.format(name))

    def write_section_using_tpl(self, name, tpl_name):
        self._write_section_separator()
        self._fobj.write(u'[{}]({})\n'.format(name, tpl_name))

    def _write_section_separator(self):
        if self._first_section:
            self._first_section = False
        else:
            self._fobj.write('\n')

    def write_option(self, name, value):
        self._fobj.write(u'{} = {}\n'.format(name, value))

    def write_options(self, options):
        for name, value in options:
            self._fobj.write(u'{} = {}\n'.format(name, value))

    def write_object_option(self, name, value):
        self._fobj.write(u'{} => {}\n'.format(name, value))
