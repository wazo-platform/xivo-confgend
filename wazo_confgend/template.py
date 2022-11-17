# -*- coding: utf-8 -*-
# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from jinja2 import Environment
from jinja2 import ChoiceLoader, PackageLoader, FileSystemLoader


def new_template_helper():
    loader = ChoiceLoader(
        [
            FileSystemLoader('/etc/wazo-confgend/templates'),
            PackageLoader(__name__, 'templates'),
        ]
    )
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
