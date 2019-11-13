# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import logging

from jinja2 import Template

logger = logging.getLogger(__name__)


class ModulesConfGenerator(object):

    def __init__(self, dependencies):
        config = dependencies['config']

        asterisk_modules = config.get('enabled_asterisk_modules', {})
        self.enabled_asterisk_modules = sorted(
            [mod for mod, enabled in asterisk_modules.items() if not enabled]
        )

        self.template_filename = config['templates']['modulesconf']

    def generate(self):
        try:
            with open(self.template_filename, 'r') as f:
                raw = f.read()
                template = Template(raw)
        except IOError as e:
            logger.error('%s', e)
            content = None
        else:
            content = template.render(modules=self.enabled_asterisk_modules)
        return content
