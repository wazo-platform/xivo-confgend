# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo.xivo_helpers import fkey_extension


class HintAdaptor(object):

    def __init__(self, dao):
        self.dao = dao

    def generate(self):
        raise NotImplementedError("hint generation must be implemented in a child class")


class ProgfunckeyAdaptor(HintAdaptor):

    def generate(self):
        progfunckey = self.dao.progfunckey_extension()
        for hint in self.find_hints():
            arguments = self.progfunckey_arguments(hint)
            extension = fkey_extension(progfunckey, arguments)
            yield (extension, 'Custom:{}'.format(extension))


class UserAdaptor(HintAdaptor):

    def generate(self):
        calluser_extension = self.dao.calluser_extension()
        for hint in self.dao.user_hints():
            calluser = '{}{}'.format(calluser_extension, hint.user_id)
            yield (hint.extension, hint.argument)
            yield (calluser, hint.argument)


class ConferenceAdaptor(HintAdaptor):

    def generate(self):
        for hint in self.dao.conference_hints():
            yield (hint.extension, 'Meetme:{}'.format(hint.extension))


class ForwardAdaptor(ProgfunckeyAdaptor):

    def find_hints(self):
        return self.dao.forward_hints()

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, hint.argument]


class ServiceAdaptor(ProgfunckeyAdaptor):

    def find_hints(self):
        return self.dao.service_hints()

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, hint.argument]


class AgentAdaptor(ProgfunckeyAdaptor):

    def find_hints(self):
        return self.dao.agent_hints()

    def progfunckey_arguments(self, hint):
        return [hint.user_id, hint.extension, '*' + hint.argument]


class CustomAdaptor(HintAdaptor):

    def generate(self):
        for hint in self.dao.custom_hints():
            yield (hint.extension, 'Custom:{}'.format(hint.extension))


class BSFilterAdaptor(HintAdaptor):

    def generate(self):
        for hint in self.dao.bsfilter_hints():
            extension = '{}{}'.format(hint.extension, hint.argument)
            yield (extension, 'Custom:{}'.format(extension))
