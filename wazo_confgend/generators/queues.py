# -*- coding: utf-8 -*-
# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later



from xivo_dao import asterisk_conf_dao

from wazo_confgend.generators.util import AsteriskFileWriter


class QueuesConf(object):

    _ignored_keys = [
        'name',
        'label',
        'category',
        'commented',
    ]

    def generate(self, output):
        queue_penalty_settings = asterisk_conf_dao.find_queue_penalty_settings()
        penalties = dict((itm['id'], itm['name']) for itm in queue_penalty_settings)

        writer = AsteriskFileWriter(output)

        writer.write_section('general')
        for item in asterisk_conf_dao.find_queue_general_settings():
            writer.write_option(item['var_name'], item['var_val'])

        for q in asterisk_conf_dao.find_queue_settings():
            writer.write_section(q['name'], comment=q['label'])

            for k, v in q.items():
                if k in self._ignored_keys:
                    continue
                if v is None or (isinstance(v, str) and not v):
                    continue

                if k == 'defaultrule':
                    if int(v) not in penalties:
                        continue
                    v = penalties[int(v)]

                writer.write_option(k, v)

            queuemember_settings = asterisk_conf_dao.find_queue_members_settings(q['name'])
            for values in queuemember_settings:
                writer.write_option('member', ','.join(values))
