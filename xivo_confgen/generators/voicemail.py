# -*- coding: utf-8 -*-
# Copyright (C) 2011-2015 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

import itertools

from xivo_confgen.generators.util import format_ast_option
from xivo_dao import asterisk_conf_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao


class VoicemailGenerator(object):

    @classmethod
    def build(cls):
        return cls(voicemail_dao.find_all_by(enabled=True))

    def __init__(self, voicemails):
        self._voicemails = voicemails

    def generate(self):
        output = u""
        for context, voicemails in self.group_voicemails():
            output += self.format_context(context)
            output += u"\n"
            output += self.format_voicemails(voicemails)
            output += u"\n\n"

        return output

    def group_voicemails(self):
        return itertools.groupby(self._voicemails, lambda v: v.context)

    def format_context(self, context):
        return u"[{}]".format(context)

    def format_voicemails(self, voicemails):
        return u"\n".join(self.format_voicemail(v) for v in voicemails)

    def format_voicemail(self, voicemail):
        parts = (voicemail.password or u'',
                 voicemail.name or u'',
                 voicemail.email or u'',
                 voicemail.pager or u'',
                 self.format_options(voicemail))

        line = u",".join(parts)

        return u"{} => {}".format(voicemail.number, line)

    def format_options(self, voicemail):
        options = []

        if voicemail.language is not None:
            options.append((u"language", voicemail.language))
        if voicemail.timezone is not None:
            options.append((u"tz", voicemail.timezone))
        if voicemail.attach_audio is not None:
            options.append((u"attach", self.format_bool(voicemail.attach_audio)))
        if voicemail.delete_messages is not None:
            options.append((u"deletevoicemail", self.format_bool(voicemail.delete_messages)))
        if voicemail.max_messages is not None:
            options.append((u"maxmsg", str(voicemail.max_messages))),

        options += voicemail.options

        options = (u"{}={}".format(key, self.escape_string(value))
                   for key, value in options)

        return u"|".join(options)

    def format_bool(self, value):
        if value is True:
            return u"yes"
        return u"no"

    def escape_string(self, value):
        return (value
                .replace(u"\n", u"\\n")
                .replace(u"\r", u"\\r")
                .replace(u"\t", u"\\t")
                .replace(u"|", u""))


class VoicemailConf(object):

    def __init__(self, voicemail_generator):
        self.voicemail_generator = voicemail_generator
        self._voicemail_settings = asterisk_conf_dao.find_voicemail_general_settings()

    def generate(self, output):
        self._gen_general_section(output)
        print >> output
        self._gen_zonemessages_section(output)
        print >> output
        print >> output, self.voicemail_generator.generate()

    def _gen_general_section(self, output):
        print >> output, u'[general]'
        for item in self._voicemail_settings:
            if item['category'] == u'general':
                opt_name = item['var_name']
                if opt_name == u'emailbody':
                    opt_val = self._format_emailbody(item['var_val'])
                else:
                    opt_val = item['var_val']
                print >> output, format_ast_option(opt_name, opt_val)

    def _format_emailbody(self, emailbody):
        return emailbody.replace(u'\n', u'\\n')

    def _gen_zonemessages_section(self, output):
        print >> output, u'[zonemessages]'
        for item in self._voicemail_settings:
            if item['category'] == u'zonemessages':
                print >> output, format_ast_option(item['var_name'], item['var_val'])
