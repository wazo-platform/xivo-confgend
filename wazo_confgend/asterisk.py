# Copyright 2010-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from io import StringIO

from xivo_dao import asterisk_conf_dao

from wazo_confgend.generators.extensionsconf import ExtensionsConf
from wazo_confgend.generators.iax import IaxConf
from wazo_confgend.generators.queues import QueuesConf
from wazo_confgend.generators.res_parking import ResParkingConf
from wazo_confgend.generators.sccp import SccpConf
from wazo_confgend.generators.util import AsteriskFileWriter
from wazo_confgend.generators.voicemail import VoicemailConf, VoicemailGenerator
from wazo_confgend.hints.generator import HintGenerator


class AsteriskFrontend:
    def __init__(self, config, tpl_helper):
        self.contextsconf = config['templates']['contextsconf']
        self._tpl_helper = tpl_helper

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
        config_generator = ExtensionsConf(
            self.contextsconf, hint_generator, self._tpl_helper
        )
        return self._generate_conf_from_generator(config_generator)

    def queues_conf(self):
        config_generator = QueuesConf()
        return self._generate_conf_from_generator(config_generator)

    def _generate_conf_from_generator(self, config_generator):
        output = StringIO()
        config_generator.generate(output)
        return output.getvalue()

    def iax_conf(self):
        config_generator = IaxConf()
        return self._generate_conf_from_generator(config_generator)

    def queueskills_conf(self):
        """Generate queueskills.conf asterisk configuration file"""
        output = StringIO()
        ast_writer = AsteriskFileWriter(output)

        agent_id = None
        for sk in asterisk_conf_dao.find_agent_queue_skills_settings():
            if agent_id != sk['id']:
                ast_writer.write_section(f"agent-{sk['id']:d}")
                agent_id = sk['id']
            ast_writer.write_option(sk['name'], sk['weight'])

        return output.getvalue()

    def queueskillrules_conf(self):
        """Generate queueskillrules.conf asterisk configuration file"""
        output = StringIO()
        ast_writer = AsteriskFileWriter(output)

        for r in asterisk_conf_dao.find_queue_skillrule_settings():
            ast_writer.write_section(f"skillrule-{r['id']}")
            if 'rule' in r and r['rule'] is not None:
                for rule in r['rule'].split(';'):
                    ast_writer.write_option('rule', rule)

        return output.getvalue()
