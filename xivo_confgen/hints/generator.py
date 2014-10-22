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

from xivo_confgen.hints import adaptor
from xivo_dao.data_handler.func_key import hint_dao


class HintGenerator(object):

    DIALPLAN = "exten = {extension},hint,{hint}"

    @classmethod
    def build(cls):
        return cls([adaptor.UserAdaptor(hint_dao),
                    adaptor.ConferenceAdaptor(hint_dao),
                    adaptor.ServiceAdaptor(hint_dao),
                    adaptor.ForwardAdaptor(hint_dao),
                    adaptor.AgentAdaptor(hint_dao),
                    adaptor.BSFilterAdaptor(hint_dao),
                    adaptor.CustomAdaptor(hint_dao)])

    def __init__(self, adaptors):
        self.adaptors = adaptors

    def generate(self, context):
        existing = set()
        for adaptor in self.adaptors:
            for extension, hint in adaptor.generate(context):
                if extension not in existing:
                    yield self.DIALPLAN.format(extension=extension,
                                               hint=hint)
                    existing.add(extension)
