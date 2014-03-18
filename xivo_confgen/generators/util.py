# -*- coding: utf-8 -*-

# Copyright (C) 2011-2014 Avencall
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
