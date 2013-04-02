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


class QueuesConf(object):

    def __init__(self, backend):
        self.backend = backend

    def generate(self, output):
        penalties = dict([(itm['id'], itm['name']) for itm in self.backend.queuepenalty.all(commented=False)])

        print >> output, '\n[general]'
        for item in self.backend.queue.all(commented=False, category='general'):
            print >> output, "%s = %s" % (item['var_name'], item['var_val'])

        for q in self.backend.queues.all(commented=False, order='name'):
            print >> output, '\n[%s]' % q['name']

            for k, v in q.iteritems():
                if k in ('name', 'category', 'commented') or v is None or \
                        (isinstance(v, (str, unicode)) and len(v) == 0):
                    continue

                if k == 'defaultrule':
                    if not int(v) in penalties:
                        continue
                    v = penalties[int(v)]

                print >> output, k, '=', v

            for m in self.backend.queuemembers.all(commented=False, queue_name=q['name'], order='position', usertype='user'):
                output.write("member => %s" % m['interface'])
                output.write(",%d" % m['penalty'])
                output.write(",")
                output.write(",%s" % m['state_interface'])
                output.write(",%s" % m['skills'])
                output.write('\n')

    @classmethod
    def new_from_backend(cls, backend):
        return cls(backend)
