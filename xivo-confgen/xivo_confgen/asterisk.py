# -*- coding: utf-8 -*-

# Copyright (C) 2010-2013 Avencall
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

from StringIO import StringIO
from xivo_confgen.generators.extensionsconf import ExtensionsConf
from xivo_confgen.generators.queues import QueuesConf
from xivo_confgen.generators.sip import SipConf
from xivo_confgen.generators.sccp import SccpConf
from xivo_confgen.generators.voicemail import VoicemailConf


class AsteriskFrontend(object):
    def __init__(self, backend):
        self.backend = backend
        self.contextsconf = None

    def sccp_conf(self):
        config_generator = SccpConf.new_from_backend(self.backend)
        return self._generate_conf_from_generator(config_generator)

    def _generate_conf_from_generator(self, config_generator):
        output = StringIO()
        config_generator.generate(output)
        return output.getvalue()

    def sip_conf(self):
        config_generator = SipConf.new_from_backend(self.backend)
        return self._generate_conf_from_generator(config_generator)

    def voicemail_conf(self):
        config_generator = VoicemailConf.new_from_backend(self.backend)
        return self._generate_conf_from_generator(config_generator)

    def extensions_conf(self):
        config_generator = ExtensionsConf.new_from_backend(self.backend, self.contextsconf)
        return self._generate_conf_from_generator(config_generator)

    def iax_conf(self):
        output = StringIO()

        # # section::general
        print >> output, self._gen_iax_general(self.backend.iax.all(commented=False))

        # # section::authentication
        items = self.backend.iaxcalllimits.all()
        if len(items) > 0:
            print >> output, '\n[callnumberlimits]'
            for auth in items:
                print >> output, "%s/%s = %s" % (auth['destination'], auth['netmask'], auth['calllimits'])

        # section::trunks
        for trunk in self.backend.iaxtrunks.all(commented=False):
            print >> output, self._gen_iax_trunk(trunk)

        # section::users
        print >> output, self._gen_iax_users(self.backend.iaxusers.all(commented=False))

        return output.getvalue()

    def _gen_iax_general(self, data_iax_general):
        output = StringIO()

        print >> output, '[general]'
        for item in data_iax_general:
            if item['var_val'] is None:
                continue

            if item['var_name'] == 'register':
                print >> output, item['var_name'], "=>", item['var_val']

            elif item['var_name'] not in ['allow', 'disallow']:
                print >> output, "%s = %s" % (item['var_name'], item['var_val'])

            elif item['var_name'] == 'allow':
                print >> output, 'disallow = all'
                for c in item['var_val'].split(','):
                    print >> output, 'allow = %s' % c

        return output.getvalue()

    def _gen_iax_users(self, data_iax_users):
        output = StringIO()

        for user in data_iax_users:
            print >> output, "\n[%s]" % user['name']

            for k, v in user.iteritems():
                if k in ('id', 'name', 'protocol', 'category', 'commented', 'initialized', 'disallow') or\
                     v in (None, ''):
                    continue

                if isinstance(v, unicode):
                    v = v.encode('utf8')

                if k == 'allow' and v != None:
                    print >> output, "disallow = all"
                    for c in v.split(','):
                        print >> output, "allow = " + str(c)
                else:
                    print >> output, k, "=", str(v)

        return output.getvalue()

    def _gen_iax_trunk(self, trunk):
        output = StringIO()

        print >> output, "\n[%s]" % trunk['name']

        for k, v in trunk.iteritems():
            if k in ('id', 'name', 'protocol', 'category', 'commented', 'disallow') or v in (None, ''):
                continue

            if isinstance(v, unicode):
                v = v.encode('utf8')

            if k == 'allow' and v != None:
                print >> output, "disallow = all"
                for c in v.split(','):
                    print >> output, "allow = " + str(c)
            else:
                print >> output, k + " = ", v

        return output.getvalue()

    def queues_conf(self):
        config_generator = QueuesConf.new_from_backend(self.backend)
        return self._generate_conf_from_generator(config_generator)

    def meetme_conf(self):
        options = StringIO()

        print >> options, '\n[general]'
        for c in self.backend.meetme.all(commented=False, category='general'):
            print >> options, "%s = %s" % (c['var_name'], c['var_val'])

        print >> options, '\n[rooms]'
        for r in self.backend.meetme.all(commented=False, category='rooms'):
            print >> options, "%s = %s" % (r['var_name'], r['var_val'])

        return options.getvalue()

    def musiconhold_conf(self):
        options = StringIO()

        cat = None
        for m in self.backend.musiconhold.all(commented=False, order='category'):
            if m['var_val'] is None:
                continue

            if m['category'] != cat:
                cat = m['category']
                print >> options, '\n[%s]' % cat

            print >> options, "%s = %s" % (m['var_name'], m['var_val'])

        return options.getvalue()

    def features_conf(self):
        options = StringIO()

        print >> options, '\n[general]'
        for f in self.backend.features.all(commented=False, category='general'):
            print >> options, "%s = %s" % (f['var_name'], f['var_val'])

        # parkinglots
        for f in self.backend.parkinglot.all(commented=False):
            print >> options, "\n[parkinglot_%s]" % f['name']
            print >> options, "context => %s" % f['context']
            print >> options, "parkext => %s" % f['extension']
            print >> options, "parkpos => %d-%d" % (int(f['extension']) + 1, int(f['extension']) + f['positions'])
            if f['next'] == 1:
                print >> options, "findslot => next"

            mmap = {
                'duration': 'parkingtime',
                'calltransfers': 'parkedcalltransfers',
                'callreparking': 'parkedcallreparking',
                'callhangup': 'parkedcallhangup',
                'callreparking': 'parkedcallreparking',
                'musicclass': 'parkedmusicclass',
                'hints': 'parkinghints',
            }
            for k, v in mmap.iteritems():
                if f[k] is not None:
                    print >> options, "%s => %s" % (v, str(f[k]))

        print >> options, '\n[featuremap]'
        for f in self.backend.features.all(commented=False, category='featuremap'):
            print >> options, "%s = %s" % (f['var_name'], f['var_val'])

        return options.getvalue()

    def queueskills_conf(self):
        """Generate queueskills.conf asterisk configuration file
        """
        options = StringIO()

        userid = None
        for sk in self.backend.userqueueskills.all():
            if userid != sk['id']:
                print >> options, "\n[user-%d]" % sk['id']
                userid = sk['id']

            print >> options, "%s = %s" % (sk['name'], sk['weight'])

        agentid = None
        for sk in self.backend.agentqueueskills.all():
            if agentid != sk['id']:
                print >> options, "\n[agent-%d]" % sk['id']
                agentid = sk['id']

            print >> options, "%s = %s" % (sk['name'], sk['weight'])

        return options.getvalue()

    def queueskillrules_conf(self):
        """Generate queueskillrules.conf asterisk configuration file
        """
        options = StringIO()

        for r in self.backend.queueskillrules.all():
            print >> options, "\n[%s]" % r['name']

            if 'rule' in r and r['rule'] is not None:
                for rule in r['rule'].split(';'):
                    print >> options, "rule = %s" % rule

        return options.getvalue()

    def queuerules_conf(self):
        options = StringIO()

        rule = None
        for m in self.backend.queuepenalties.all():
            if m['name'] != rule:
                rule = m['name']
                print >> options, "\n[%s]" % rule

            print >> options, "penaltychange => %d," % m['seconds'],
            if m['maxp_sign'] is not None and m['maxp_value'] is not None:
                sign = '' if m['maxp_sign'] == '=' else m['maxp_sign']
                print >> options, "%w%d" % (sign, m['maxp_value']),

            if m['minp_sign'] is not None and m['minp_value'] is not None:
                sign = '' if m['minp_sign'] == '=' else m['minp_sign']
                print >> options, ",%s%d" % (sign, m['minp_value']),

            print >> options

        return options.getvalue()
