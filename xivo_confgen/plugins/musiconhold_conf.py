# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

from __future__ import unicode_literals

from xivo_dao.resources.moh import dao as moh_dao


class MOHConfGenerator(object):

    def __init__(self, dependencies):
        self._tpl_helper = dependencies['tpl_helper']

    def generate(self):
        template_context = {
            'base_directory': '/var/lib/asterisk/moh',
            'moh_list': moh_dao.find_all_by(),
            'sort_map': {
                'alphabetical': 'alpha',
                'random_start': 'randstart',
            },
        }
        template = self._tpl_helper.get_template('asterisk/musiconhold')
        return template.dump(template_context)
