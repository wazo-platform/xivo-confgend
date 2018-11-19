# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confgen.generators.util import (
    format_ast_option,
    format_ast_object_option,
)
from xivo_dao import asterisk_conf_dao


class QueuesConf(object):

    def generate(self, output):
        queue_penalty_settings = asterisk_conf_dao.find_queue_penalty_settings()
        penalties = dict((itm['id'], itm['name']) for itm in queue_penalty_settings)

        print >> output, '[general]'
        for item in asterisk_conf_dao.find_queue_general_settings():
            print >> output, format_ast_option(item['var_name'], item['var_val'])

        for q in asterisk_conf_dao.find_queue_settings():
            print >> output, '\n[%s]' % q['name']

            for k, v in q.iteritems():
                if k in ('name', 'category', 'commented') or v is None or \
                        (isinstance(v, basestring) and not v):
                    continue

                if k == 'defaultrule':
                    if int(v) not in penalties:
                        continue
                    v = penalties[int(v)]

                print >> output, format_ast_option(k, v)

            queuemember_settings = asterisk_conf_dao.find_queue_members_settings(q['name'])
            for m in queuemember_settings:
                interface = m['interface']
                # TODO clean after pjsip migration
                if interface.startswith('SIP/'):
                    interface = interface.replace('SIP', 'PJSIP')
                member_value = '%s,%d' % (interface, m['penalty'])
                print >> output, format_ast_object_option('member', member_value)
