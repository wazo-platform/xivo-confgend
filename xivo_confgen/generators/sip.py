# -*- coding: utf-8 -*-

# Copyright (C) 2011-2014 Avencall
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

from xivo_dao import asterisk_conf_dao

CC_POLICY_ENABLED = 'generic'
CC_POLICY_DISABLED = 'never'
CC_OFFER_TIMER = 30
CC_RECALL_TIMER = 20
CCBS_AVAILABLE_TIMER = 900
CCNR_AVAILABLE_TIMER = 900


class SipConf(object):

    def generate(self, output):
        data_general = asterisk_conf_dao.find_sip_general_settings()
        self._gen_general(data_general, output)
        print >> output

        data_auth = asterisk_conf_dao.find_sip_authentication_settings()
        self._gen_authentication(data_auth, output)
        print >> output

        data_trunk = asterisk_conf_dao.find_sip_trunk_settings()
        self._gen_trunk(data_trunk, output)
        print >> output

        data_pickup = asterisk_conf_dao.find_sip_pickup_settings()
        data_user = asterisk_conf_dao.find_sip_user_settings()
        data_ccss = asterisk_conf_dao.find_extenfeatures_settings(['cctoggle'])
        ccss_options = self._ccss_options(data_ccss)
        self._gen_user(data_pickup, data_user, ccss_options, output)

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
                for c in item['var_val'].split(','):
                    print >> output, 'allow = %s' % c

    def _gen_authentication(self, data_authentication, output):
        if len(data_authentication) > 0:
            print >> output, '\n[authentication]'
            for auth in data_authentication:
                mode = '#' if auth['secretmode'] == 'md5' else ':'
                print >> output, "auth = %s%s%s@%s" % (auth['user'], mode, auth['secret'], auth['realm'])

    def _gen_trunk(self, data_trunk, output):
        for trunk in data_trunk:
            print >> output, "\n[%s]" % trunk['name']

            for k, v in trunk.iteritems():
                if k in ('id', 'name', 'protocol', 'category', 'commented', 'disallow') or v in (None, ''):
                    continue

                if isinstance(v, unicode):
                    v = v.encode('utf8')

                if k == 'allow':
                    print >> output, "disallow = all"
                    for c in v.split(','):
                        print >> output, "allow = " + str(c)
                else:
                    print >> output, k, '=', v

    def _gen_user(self, data_pickup, data_user, ccss_options, output):
        sip_unused_values = (
            'id', 'name', 'protocol',
            'category', 'commented', 'initialized',
            'disallow', 'regseconds', 'lastms',
            'name', 'fullcontact', 'ipaddr', 'number'
        )

        pickups = {}
        for p in data_pickup:
            user = pickups.setdefault(p[0], {})
            user.setdefault(p[1], []).append(str(p[2]))

        for user in data_user:
            print >> output, "\n[%s]" % user['name']

            for key, value in user.iteritems():
                if key in sip_unused_values or value in (None, ''):
                    continue

                if key not in ('allow', 'subscribemwi'):
                    print >> output, gen_value_line(key, value)

                if key == 'allow':
                    print >> output, gen_value_line('disallow', 'all')
                    for codec in value.split(','):
                        print >> output, gen_value_line("allow", codec)

                if key == 'subscribemwi':
                    value = 'no' if value == 0 else 'yes'
                    print >> output, gen_value_line('subscribemwi', value)

            print >> output, gen_value_line('setvar', 'PICKUPMARK=%s%%%s' % (user['number'], user['context']))
            print >> output, gen_value_line('setvar', 'TRANSFER_CONTEXT=%s' % user['context'])

            if user['name'] in pickups:
                p = pickups[user['name']]
                # WARNING:
                # pickupgroup: trappable calls  (xivo members)
                # callgroup  : can pickup calls (xivo pickups)
                if 'member' in p:
                    print >> output, "pickupgroup = " + ','.join(frozenset(p['member']))
                if 'pickup' in p:
                    print >> output, "callgroup = " + ','.join(frozenset(p['pickup']))

            for ccss_option, value in ccss_options.iteritems():
                print >> output, gen_value_line(ccss_option, value)

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
