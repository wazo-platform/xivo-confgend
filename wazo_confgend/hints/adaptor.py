# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
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
    def __init__(self, dao):
        super().__init__(dao)
        self._hints = self.dao.user_hints()

    def generate(self, context):
        hints = self._hints.get(context) or []
        for hint in hints:
            yield (hint.extension, hint.argument)


class UserSharedHintAdaptor(HintAdaptor):
    def generate(self):
        for hint in self.dao.user_shared_hints():
            yield (hint.extension, hint.argument)


class ConferenceAdaptor(HintAdaptor):
    def __init__(self, dao):
        super().__init__(dao)
        self._hints = self.dao.conference_hints()

    def generate(self, context):
        hints = self._hints.get(context) or []
        for hint in hints:
            yield (hint.extension, f'confbridge:{hint.conference_id}')


class ForwardAdaptor(ProgfunckeyAdaptor):
    def __init__(self, dao):
        super().__init__(dao)
        self._hints = self.dao.forward_hints()

    def find_hints(self, context):
        return self._hints.get(context) or []

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, hint.argument]


class GroupMemberAdaptor(ProgfunckeyAdaptor):
    def __init__(self, dao):
        super().__init__(dao)
        self._hints = self.dao.groupmember_hints()

    def find_hints(self, context):
        return self._hints.get(context) or []

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, hint.argument]


class ServiceAdaptor(ProgfunckeyAdaptor):
    def __init__(self, dao):
        super().__init__(dao)
        self._hints = self.dao.service_hints()

    def find_hints(self, context):
        return self._hints.get(context) or []

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, hint.argument]


class AgentAdaptor(ProgfunckeyAdaptor):
    def __init__(self, dao):
        super().__init__(dao)
        self._hints = self.dao.agent_hints()

    def find_hints(self, context):
        return self._hints.get(context) or []

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, '*' + hint.argument]


class CustomAdaptor(HintAdaptor):
    def __init__(self, dao):
        super().__init__(dao)
        self._hints = self.dao.custom_hints()

    def generate(self, context):
        hints = self._hints.get(context) or []
        for hint in hints:
            try:
                yield (hint.extension, f'Custom:{hint.extension}')
            except UnicodeEncodeError:
                logger.info('invalid custom function key "%s"', hint.extension)
                continue


class BSFilterAdaptor(HintAdaptor):
    def __init__(self, dao):
        super().__init__(dao)
        self._hints = self.dao.bsfilter_hints()

    def generate(self, context):
        hints = self._hints.get(context) or []
        for hint in hints:
            extension = f'{hint.extension}{hint.argument}'
            yield (extension, f'Custom:{extension}')
