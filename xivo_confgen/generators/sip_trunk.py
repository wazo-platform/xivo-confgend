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


class SipTrunkGenerator(object):

    EXCLUDE_OPTIONS = ('id',
                       'name',
                       'commented',
                       'protocol',
                       'category',
                       'disallow')

    def __init__(self, dao):
        self.dao = dao

    def generate(self):
        trunks = self.dao.find_all_by(commented=0, category='trunk')
        for trunk in trunks:
            for line in self.format_trunk(trunk):
                yield line

    def format_trunk(self, trunk):
        options = trunk.all_options(exclude=self.EXCLUDE_OPTIONS)
        allow_present = 'allow' in (option_name for option_name, _ in options)

        yield '[{}]'.format(trunk.name)

        if allow_present:
            yield 'disallow = all'

        for name, value in options:
            yield '{} = {}'.format(name, value)

        yield ''
