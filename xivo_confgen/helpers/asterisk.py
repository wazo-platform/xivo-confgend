# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals


class AsteriskFileGenerator(object):

    def __init__(self, dao):
        self.asterisk_file_dao = dao

    def generate(self, name, output):
        file_ = self.asterisk_file_dao.find_by(name=name)
        self._generate_file(file_, output)

    def _generate_file(self, file_, output):
        if not file_:
            return

        for section in file_.sections_ordered:
            print >> output, '[{}]'.format(section.name)
            for variable in section.variables:
                print >> output, '{} = {}'.format(variable.key,
                                                  variable.value if variable.value else '')
            print >> output
