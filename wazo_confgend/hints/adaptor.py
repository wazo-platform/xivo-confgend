# Copyright 2014-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo.xivo_helpers import fkey_extension

logger = logging.getLogger(__name__)


class HintAdaptor:
    def __init__(self, dao):
        self.dao = dao

    def generate(self, context):
        raise NotImplementedError(
            "hint generation must be implemented in a child class"
        )


class ProgfunckeyAdaptor(HintAdaptor):
    def generate(self, context):
        progfunckey = self.dao.progfunckey_extension()
        for hint in self.find_hints(context):
            arguments = self.progfunckey_arguments(hint)
            extension = fkey_extension(progfunckey, arguments)
            yield (extension, f'Custom:{extension}')


class UserAdaptor(HintAdaptor):
    def generate(self, context):
        for hint in self.dao.user_hints(context):
            yield (hint.extension, hint.argument)


class UserSharedHintAdaptor(HintAdaptor):
    def generate(self):
        for hint in self.dao.user_shared_hints():
            yield (hint.extension, hint.argument)


class ConferenceAdaptor(HintAdaptor):
    def generate(self, context):
        for hint in self.dao.conference_hints(context):
            yield (hint.extension, f'confbridge:{hint.conference_id}')


class ForwardAdaptor(ProgfunckeyAdaptor):
    def find_hints(self, context):
        return self.dao.forward_hints(context)

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, hint.argument]


class GroupMemberAdaptor(ProgfunckeyAdaptor):
    def find_hints(self, context):
        return self.dao.groupmember_hints(context)

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, hint.argument]


class ServiceAdaptor(ProgfunckeyAdaptor):
    def find_hints(self, context):
        return self.dao.service_hints(context)

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, hint.argument]


class AgentAdaptor(ProgfunckeyAdaptor):
    def find_hints(self, context):
        return self.dao.agent_hints(context)

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, '*' + hint.argument]


class CustomAdaptor(HintAdaptor):
    def generate(self, context):
        for hint in self.dao.custom_hints(context):
            try:
                yield (hint.extension, f'Custom:{hint.extension}')
            except UnicodeEncodeError:
                logger.info('invalid custom function key "%s"', hint.extension)
                continue


class BSFilterAdaptor(HintAdaptor):
    def generate(self, context):
        for hint in self.dao.bsfilter_hints(context):
            extension = f'{hint.extension}{hint.argument}'
            yield (extension, f'Custom:{extension}')
