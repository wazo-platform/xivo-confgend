# -*- coding: UTF-8 -*-

import unittest
import StringIO
from mock import Mock, patch
from xivo_confgen.generators.agents_conf import AgentsConf


class TestAgents(unittest.TestCase):

    def assertConfigEqual(self, configExpected, configResult):
        self.assertEqual(configExpected.replace(' ', ''), configResult.replace(' ', ''))

    def setUp(self):
        self._output = StringIO.StringIO()

    generate_general = Mock()

    @patch.object(AgentsConf, '_generate_general')
    @patch.object(AgentsConf, '_generate_agent_global_params')
    @patch.object(AgentsConf, '_generate_agents')
    def testGenerate(self, generate_general, generate_agent_global_params, generate_agents):

        agents_conf = AgentsConf([], [], [])

        agents_conf.generate(self._output)

        generate_general.assert_called_with(self._output)
        generate_agent_global_params.assert_called_with(self._output)
        generate_agents.assert_called_with(self._output)

    def test_general_section(self):
        agent_general_db = [
            {'category': u'general', 'option_name': u'multiplelogin', 'option_value': u'no'},
        ]

        expected = """\
                    [general]
                    multiplelogin = no

                   """

        agents_conf = AgentsConf(agent_general_db, [], [])

        agents_conf._generate_general(self._output)

        self.assertConfigEqual(expected, self._output.getvalue())

    def test_agent_global_params(self):
        agent_global_params_db = [
            {'category': u'agents', 'option_name': u'maxlogintries', 'option_value': u'3'},
            {'category': u'agents', 'option_name': u'foobar', 'option_value': u'abc'},
        ]

        expected = """\
                    [agents]
                    maxlogintries = 3
                    foobar = abc

                   """

        agents_conf = AgentsConf([], agent_global_params_db, [])

        agents_conf._generate_agent_global_params(self._output)

        self.assertConfigEqual(expected, self._output.getvalue())

    def test_agents_section(self):
        agent_db = [
            {'firstname':u'John', 'lastname':u'Wayne', 'number':u'3456', 'passwd': u'0022',
             'autologoff':u'0', 'wrapuptime':u'30000'},
            {'firstname':u'Alfred', 'lastname':u'Bourne', 'number':u'7766', 'passwd': u'',
             'autologoff':u'0', 'wrapuptime':u'50000'}
        ]

        expected = """\
                    autologoff = 0
                    wrapuptime = 30000
                    agent => 3456,0022,John Wayne

                    autologoff = 0
                    wrapuptime = 50000
                    agent => 7766,,Alfred Bourne

                   """
        agents_conf = AgentsConf([], [], agent_db)

        agents_conf._generate_agents(self._output)

        self.assertConfigEqual(expected, self._output.getvalue())
