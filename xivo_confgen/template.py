# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from jinja2 import Environment
from jinja2 import ChoiceLoader, PackageLoader, FileSystemLoader


def new_template_helper():
    loader = ChoiceLoader([
        FileSystemLoader('/etc/xivo-confgend/templates'),
        PackageLoader(__name__, 'templates'),
    ])
    return TemplateHelper(loader)


class TemplateHelper(object):

    def __init__(self, loader):
        self._env = Environment(loader=loader)

    def get_template(self, name):
        filename = '{}.jinja'.format(name)
        return _Template(self._env.get_template(filename))

    def get_customizable_template(self, name, custom_part):
        filename = '{}.jinja'.format(name)
        filename_custom = '{}-{}.jinja'.format(name, custom_part)
        return _Template(self._env.select_template([filename_custom, filename]))

    def get_legacy_contexts_conf(self):
        # TODO return contextsconf as an OrderedRawConf like previously...
        pass


class _Template(object):

    def __init__(self, jinja_template):
        self._jinja_template = jinja_template

    def dump(self, context):
        # XXX do we encode in utf-8 ?
        return self._jinja_template.render(context)

    def generate(self, context, output):
        self._jinja_template.stream(context).dump(output, encoding='utf-8')
