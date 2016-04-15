# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016 Avencall
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

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import asterisk_conf_dao

CC_POLICY_ENABLED = 'generic'
CC_POLICY_DISABLED = 'never'
CC_OFFER_TIMER = 30
CC_RECALL_TIMER = 20
CCBS_AVAILABLE_TIMER = 900
CCNR_AVAILABLE_TIMER = 900


class SipConf(object):

    def __init__(self, trunk_generator, user_generator):
        self.trunk_generator = trunk_generator
        self.user_generator = user_generator

    def generate(self, output):
        with session_scope():
            self._generate(output)

    def _generate(self, output):
        data_general = asterisk_conf_dao.find_sip_general_settings()
        self._gen_general(data_general, output)
        print >> output

        data_auth = asterisk_conf_dao.find_sip_authentication_settings()
        self._gen_authentication(data_auth, output)
        print >> output

        self._gen_trunk(output)
        print >> output

        data_ccss = asterisk_conf_dao.find_extenfeatures_settings(['cctoggle'])
        ccss_options = self._ccss_options(data_ccss)
        self._gen_user(ccss_options, output)

        print >> output

    def _gen_general(self, data_general, output):
        print >> output, '[general]'
        for item in data_general:
            if item['var_val'] is None:
                continue

            if item['var_name'] in ('register', 'mwi'):
                print >> output, item['var_name'], "=>", item['var_val']

            elif item['var_name'] == 'prematuremedia':
                var_val = 'yes' if item['var_val'] == 'no' else 'no'
                print >> output, item['var_name'], "=", var_val

            elif item['var_name'] not in ['allow', 'disallow']:
                print >> output, item['var_name'], "=", item['var_val']

            elif item['var_name'] == 'allow':
                print >> output, 'disallow = all'
                print >> output, 'allow =', item['var_val']

    def _gen_authentication(self, data_authentication, output):
        if len(data_authentication) > 0:
            print >> output, '\n[authentication]'
            for auth in data_authentication:
                mode = '#' if auth['secretmode'] == 'md5' else ':'
                print >> output, "auth = %s%s%s@%s" % (auth['user'], mode, auth['secret'], auth['realm'])

    def _gen_trunk(self, output):
        for line in self.trunk_generator.generate():
            print >> output, line

    def _gen_user(self, ccss_options, output):
        for line in self.user_generator.generate(ccss_options):
            print >> output, line

    def _ccss_options(self, data_ccss):
        if data_ccss:
            ccss_info = data_ccss[0]
            if ccss_info.get('commented') == 0:
                return {
                    'cc_agent_policy': CC_POLICY_ENABLED,
                    'cc_monitor_policy': CC_POLICY_ENABLED,
                    'cc_offer_timer': CC_OFFER_TIMER,
                    'cc_recall_timer': CC_RECALL_TIMER,
                    'ccbs_available_timer': CCBS_AVAILABLE_TIMER,
                    'ccnr_available_timer': CCNR_AVAILABLE_TIMER,
                }

        return {
            'cc_agent_policy': CC_POLICY_DISABLED,
            'cc_monitor_policy': CC_POLICY_DISABLED,
        }


def gen_value_line(key, value):
    return u'%s = %s' % (key, unicodify_string(value))


def unicodify_string(to_unicodify):
    try:
        return unicode(to_unicodify)
    except UnicodeDecodeError:
        return to_unicodify.decode('utf8')
