# -*- coding: utf-8 -*-
# Copyright 2010-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from StringIO import StringIO

from xivo_confgen.generators.extensionsconf import ExtensionsConf
from xivo_confgen.generators.features import FeaturesConf
from xivo_confgen.generators.queues import QueuesConf
from xivo_confgen.generators.res_parking import ResParkingConf
from xivo_confgen.generators.sccp import SccpConf
from xivo_confgen.generators.voicemail import VoicemailConf, VoicemailGenerator
from xivo_confgen.hints.generator import HintGenerator
from xivo_dao import asterisk_conf_dao


class AsteriskFrontend(object):

    def __init__(self, config, tpl_helper):
        self.contextsconf = config['templates']['contextsconf']
        self._tpl_helper = tpl_helper

    def features_conf(self):
        config_generator = FeaturesConf()
        return self._generate_conf_from_generator(config_generator)

    def res_parking_conf(self):
        config_generator = ResParkingConf()
        return self._generate_conf_from_generator(config_generator)

    def sccp_conf(self):
        config_generator = SccpConf()
        return self._generate_conf_from_generator(config_generator)

    def voicemail_conf(self):
        voicemail_generator = VoicemailGenerator.build()
        config_generator = VoicemailConf(voicemail_generator)
        return self._generate_conf_from_generator(config_generator)

    def extensions_conf(self):
        hint_generator = HintGenerator.build()
        config_generator = ExtensionsConf(self.contextsconf, hint_generator, self._tpl_helper)
        return self._generate_conf_from_generator(config_generator)

    def queues_conf(self):
        config_generator = QueuesConf()
        return self._generate_conf_from_generator(config_generator)

    def _generate_conf_from_generator(self, config_generator):
        output = StringIO()
        config_generator.generate(output)
        return output.getvalue()

    def iax_conf(self):
        output = StringIO()

        # # section::general
        data_iax_general_settings = asterisk_conf_dao.find_iax_general_settings()
        print >> output, self._gen_iax_general(data_iax_general_settings)

        # # section::callnumberlimits
        items = asterisk_conf_dao.find_iax_calllimits_settings()
        if len(items) > 0:
            print >> output, '\n[callnumberlimits]'
            for auth in items:
                print >> output, "%s/%s = %s" % (auth['destination'], auth['netmask'], auth['calllimits'])

        # section::trunks
        for trunk in asterisk_conf_dao.find_iax_trunk_settings():
            print >> output, self._gen_iax_trunk(trunk)

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

    def _gen_iax_trunk(self, trunk):
        output = StringIO()

        print >> output, "\n[%s]" % trunk.name

        exclude_options = ('id', 'name', 'protocol', 'category', 'commented', 'disallow')
        for k, v in trunk.all_options(exclude=exclude_options):
            if v in (None, ''):
                continue

            if isinstance(v, unicode):
                v = v.encode('utf8')

            if k == 'allow':
                print >> output, "disallow = all"
                for c in v.split(','):
                    print >> output, "allow = " + str(c)
            else:
                print >> output, k + " = ", v

        return output.getvalue()

    def meetme_conf(self):
        options = StringIO()

        print >> options, '\n[general]'
        for c in asterisk_conf_dao.find_meetme_general_settings():
            print >> options, "%s = %s" % (c['var_name'], c['var_val'])

        print >> options, '\n[rooms]'
        for r in asterisk_conf_dao.find_meetme_rooms_settings():
            print >> options, "%s = %s" % (r['var_name'], r['var_val'])

        return options.getvalue()

    def queueskills_conf(self):
        """Generate queueskills.conf asterisk configuration file
        """
        options = StringIO()

        agentid = None
        for sk in asterisk_conf_dao.find_agent_queue_skills_settings():
            if agentid != sk['id']:
                print >> options, "\n[agent-%d]" % sk['id']
                agentid = sk['id']

            print >> options, "%s = %s" % (sk['name'], sk['weight'])

        return options.getvalue()

    def queueskillrules_conf(self):
        """Generate queueskillrules.conf asterisk configuration file
        """
        options = StringIO()

        for r in asterisk_conf_dao.find_queue_skillrule_settings():
            print >> options, "\n[skillrule-%s]" % r['id']

            if 'rule' in r and r['rule'] is not None:
                for rule in r['rule'].split(';'):
                    print >> options, "rule = %s" % rule

        return options.getvalue()

    def queuerules_conf(self):
        options = StringIO()

        rule = None
        for m in asterisk_conf_dao.find_queue_penalties_settings():
            if m['name'] != rule:
                rule = m['name']
                print >> options, "\n[%s]" % rule

            print >> options, "penaltychange => %d," % m['seconds'],
            if m['maxp_sign'] is not None and m['maxp_value'] is not None:
                sign = '' if m['maxp_sign'] == '=' else m['maxp_sign']
                print >> options, "%s%d" % (sign, m['maxp_value']),

            if m['minp_sign'] is not None and m['minp_value'] is not None:
                sign = '' if m['minp_sign'] == '=' else m['minp_sign']
                print >> options, ",%s%d" % (sign, m['minp_value']),

            print >> options

        return options.getvalue()
