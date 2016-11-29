# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

import unittest
from mock import Mock

from StringIO import StringIO

from xivo_confgen.generators.tests.util import assert_config_equal
from xivo_confgen.generators.tests.util import assert_section_equal

from ..sip_conf import (
    _SipTrunkGenerator,
    _SipUserGenerator,
    _SipConf,
    gen_value_line,
    unicodify_string,
    CC_OFFER_TIMER,
    CC_RECALL_TIMER,
    CCBS_AVAILABLE_TIMER,
    CCNR_AVAILABLE_TIMER,
)


class TestSipConf(unittest.TestCase):

    def setUp(self):
        self.trunk_generator = Mock(_SipTrunkGenerator)
        self.user_generator = Mock(_SipUserGenerator)
        self.sip_conf = _SipConf(self.trunk_generator, self.user_generator)
        self.output = StringIO()

    def test_get_line(self):
        result = gen_value_line('emailbody', 'pépè')
        self.assertEqual(result, u'emailbody = pépè')

    def test_unicodify_string(self):
        self.assertEqual(u'pépé', unicodify_string(u'pépé'))
        self.assertEqual(u'pépé', unicodify_string(u'pépé'.encode('utf8')))
        self.assertEqual(u'pépé', unicodify_string('pépé'))
        self.assertEqual(u'8', unicodify_string(8))

    def test_gen_general(self):
        staticsip = [
            {'filename': u'sip.conf', 'category': u'general', 'var_name': u'autocreate_prefix', 'var_val': u'apv6Ym3fJW'},
            {'filename': u'sip.conf', 'category': u'general', 'var_name': u'language', 'var_val': u'fr_FR'},
            {'filename': u'sip.conf', 'category': u'general', 'var_name': u'jbtargetextra', 'var_val': None},
            {'filename': u'sip.conf', 'category': u'general', 'var_name': u'notifycid', 'var_val': u'no'},
            {'filename': u'sip.conf', 'category': u'general', 'var_name': u'session-expires', 'var_val': u'600'},
            {'filename': u'sip.conf', 'category': u'general', 'var_name': u'vmexten', 'var_val': u'*98'},
        ]

        self.sip_conf._gen_general(staticsip, self.output)

        assert_config_equal(self.output.getvalue(), '''
            [general]
            autocreate_prefix = apv6Ym3fJW
            language = fr_FR
            notifycid = no
            session-expires = 600
            vmexten = *98
        ''')

    def test_gen_authentication(self):
        sipauthentication = [{'id': 1, 'usersip_id': None, 'user': u'test', 'secretmode': u'md5',
                              'secret': u'test', 'realm': u'test.com'}]

        self.sip_conf._gen_authentication(sipauthentication, self.output)

        assert_config_equal(self.output.getvalue(), '''
            [authentication]
            auth = test#test@test.com
        ''')

    def test_gen_trunk(self):
        self.trunk_generator.generate.return_value = [
            u'[trûnksip]',
            u'amaflags = default',
            u'call-limit = 10',
            u'host = dynamic',
            u'type = peer',
            u'subscribemwi = no',
        ]

        self.sip_conf._gen_trunk(self.output)

        assert_section_equal(self.output.getvalue(), u'''
            [trûnksip]
            amaflags = default
            call-limit = 10
            host = dynamic
            type = peer
            subscribemwi = no
        ''')

    def test_gen_authentication_empty(self):
        sipauthentication = []

        self.sip_conf._gen_authentication(sipauthentication, self.output)

        self.assertEqual(u'', self.output.getvalue())

    def test_gen_user(self):
        self.user_generator.generate.return_value = [
            u'[usèr]',
            u'secret = secret',
            u'host = dynamic',
            u'type = friend',
        ]

        self.sip_conf._gen_user({}, self.output)

        assert_section_equal(self.output.getvalue(), u'''
            [usèr]
            secret = secret
            host = dynamic
            type = friend
        ''')

    def test__ccss_options_enabled(self):
        data_ccss = [{'commented': 0}]

        ccss_options = self.sip_conf._ccss_options(data_ccss)

        self.assertEqual('generic', ccss_options['cc_agent_policy'])
        self.assertEqual('generic', ccss_options['cc_monitor_policy'])
        self.assertEqual(CC_OFFER_TIMER, ccss_options['cc_offer_timer'])
        self.assertEqual(CC_RECALL_TIMER, ccss_options['cc_recall_timer'])
        self.assertEqual(CCBS_AVAILABLE_TIMER, ccss_options['ccbs_available_timer'])
        self.assertEqual(CCNR_AVAILABLE_TIMER, ccss_options['ccnr_available_timer'])

    def test__ccss_options_disabled(self):
        data_ccss = [{'commented': 1}]

        ccss_options = self.sip_conf._ccss_options(data_ccss)

        self.assertEqual('never', ccss_options['cc_agent_policy'])
        self.assertEqual('never', ccss_options['cc_monitor_policy'])
        self.assertNotIn('cc_offer_timer', ccss_options)
        self.assertNotIn('cc_recall_timer', ccss_options)
        self.assertNotIn('ccbs_available_timer', ccss_options)
        self.assertNotIn('ccnr_available_timer', ccss_options)
