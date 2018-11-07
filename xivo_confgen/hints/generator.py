# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confgen.hints import adaptor as hint_adaptor
from xivo_dao.resources.func_key import hint_dao


class HintGenerator(object):

    DIALPLAN = "exten = {extension},hint,{hint}"

    @classmethod
    def build(cls):
        return cls([hint_adaptor.UserAdaptor(hint_dao),
                    hint_adaptor.ConferenceAdaptor(hint_dao),
                    hint_adaptor.ServiceAdaptor(hint_dao),
                    hint_adaptor.ForwardAdaptor(hint_dao),
                    hint_adaptor.AgentAdaptor(hint_dao),
                    hint_adaptor.BSFilterAdaptor(hint_dao),
                    hint_adaptor.CustomAdaptor(hint_dao)])

    def __init__(self, adaptors):
        self.adaptors = adaptors

    def generate(self, context):
        existing = set()
        for adaptor in self.adaptors:
            for extension, hint in adaptor.generate(context):
                # TODO clean after pjsip migration
                if hint.startswith('SIP'):
                    hint = hint.replace('SIP', 'PJSIP')
                if extension not in existing:
                    yield self.DIALPLAN.format(extension=extension,
                                               hint=hint)
                    existing.add(extension)
