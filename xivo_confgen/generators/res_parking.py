# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_confgen.generators.util import AsteriskFileWriter
from xivo_dao import asterisk_conf_dao


class ResParkingConf(object):

    def __init__(self):
        self._settings = asterisk_conf_dao.find_parking_settings()

    def generate(self, output):
        ast_file = AsteriskFileWriter(output)
        self._generate_general(ast_file)
        self._generate_parking_lots(ast_file)

    def _generate_general(self, ast_file):
        ast_file.write_section(u'general')
        ast_file.write_options(self._settings['general_options'])

    def _generate_parking_lots(self, ast_file):
        for parking_lot in self._settings['parking_lots']:
            ast_file.write_section(parking_lot['name'])
            ast_file.write_options(parking_lot['options'])
