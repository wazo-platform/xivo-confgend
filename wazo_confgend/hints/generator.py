# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confgend.hints import adaptor as hint_adaptor
from xivo_dao.resources.func_key import hint_dao


class HintGenerator(object):

    DIALPLAN = "exten = {extension},hint,{hint}"

    @classmethod
    def build(cls):
        context_resource_adaptors = [
            hint_adaptor.UserAdaptor(hint_dao),
            hint_adaptor.ConferenceAdaptor(hint_dao),
            hint_adaptor.ServiceAdaptor(hint_dao),
            hint_adaptor.ForwardAdaptor(hint_dao),
            hint_adaptor.GroupMemberAdaptor(hint_dao),
            hint_adaptor.AgentAdaptor(hint_dao),
            hint_adaptor.BSFilterAdaptor(hint_dao),
            hint_adaptor.CustomAdaptor(hint_dao),
        ]
        global_resource_adaptors = [
            hint_adaptor.UserSharedHintAdaptor(hint_dao),
        ]

        return cls(
            context_resource_adaptors,
            global_resource_adaptors,
        )

    def __init__(self, context_resource_adaptors, global_resource_adaptors):
        self.context_resource_adaptors = context_resource_adaptors
        self.global_resource_adaptors = global_resource_adaptors

    def generate_global_hints(self):
        for adaptor in self.global_resource_adaptors:
            for extension, hint in adaptor.generate():
                yield self.DIALPLAN.format(extension=extension, hint=hint)

    def generate(self, context):
        existing = set()
        for adaptor in self.context_resource_adaptors:
            for extension, hint in adaptor.generate(context):
                if extension not in existing:
                    yield self.DIALPLAN.format(extension=extension, hint=hint)
                    existing.add(extension)
