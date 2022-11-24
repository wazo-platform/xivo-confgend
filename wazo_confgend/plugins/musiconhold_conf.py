# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


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
