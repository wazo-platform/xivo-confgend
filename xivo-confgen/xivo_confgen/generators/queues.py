# -*- coding: utf-8 -*-

# Copyright (C) 2013  Avencall
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

from xivo_confgen.generators.util import format_ast_option, \
    format_ast_object_option
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
                member_value = '%s,%d' % (m['interface'], m['penalty'])
                print >> output, format_ast_object_option('member', member_value)
