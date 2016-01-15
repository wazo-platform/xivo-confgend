# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import unicode_literals


class SipUserGenerator(object):

    EXCLUDE = ('name',
               'protocol',
               'category',
               'initialized',
               'disallow',
               'regseconds',
               'lastms',
               'name',
               'fullcontact',
               'ipaddr')

    def __init__(self, dao):
        self.dao = dao

    def generate(self, ccss_options):
        for row in self.dao.find_sip_user_settings():
            for line in self.format_row(row, ccss_options):
                yield line

    def format_row(self, row, ccss_options):
        yield '[{}]'.format(row.UserSIP.name)

        for line in self.format_user_options(row):
            yield line
        for line in self.format_options(ccss_options.iteritems()):
            yield line

        options = row.UserSIP.all_options(self.EXCLUDE)
        for line in self.format_allow_options(options):
            yield line
        for line in self.format_options(options):
            yield line

        yield ''

    def format_user_options(self, row):
        if row.context:
            yield 'setvar = TRANSFER_CONTEXT={}'.format(row.context)
        if row.number and row.context:
            yield 'setvar = PICKUPMARK={}%{}'.format(row.number, row.context)
        if row.uuid:
            yield 'setvar = XIVO_USERUUID={}'.format(row.uuid)
        if row.namedpickupgroup:
            yield 'namedpickupgroup = {}'.format(row.namedpickupgroup)
        if row.namedpickupgroup:
            yield 'namedcallgroup = {}'.format(row.namedcallgroup)
        if row.mohsuggest:
            yield 'mohsuggest = {}'.format(row.mohsuggest)
        if row.UserSIP.callerid:
            yield 'description = {}'.format(row.UserSIP.callerid)

    def format_allow_options(self, options):
        allow_found = any(1 for name, value in options if name == "allow")
        if allow_found:
            yield 'disallow = all'

    def format_options(self, options):
        for name, value in options:
            yield '{} = {}'.format(name, value)
