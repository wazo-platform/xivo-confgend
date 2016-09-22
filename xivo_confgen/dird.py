# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
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

import yaml

from xivo_dao import cti_context_dao
from xivo_dao import cti_displays_dao
from xivo_dao import cti_main_dao
from xivo_dao import cti_reverse_dao


class _ContextSeparatedMixin(object):

    _context_separated_types = ['xivo']

    def source_name(self, profile, name, type_):
        if type_ in self._context_separated_types:
            return '{}_{}'.format(name, profile)
        return name


class _AssociationGenerator(object):

    def generate(self):
        raw = cti_displays_dao.get_profile_configuration()
        return {profile: config['display']
                for profile, config in raw.iteritems()}


class _PhoneAssociationGenerator(object):

    _DEFAULT_PHONE_DISPLAY = 'default'

    def generate(self):
        profiles = cti_context_dao.get_context_names()
        return {profile: self._DEFAULT_PHONE_DISPLAY for profile in profiles}


class _DisplayGenerator(object):

    _fields = ['title', 'type', 'default', 'field']

    def generate(self):
        raw = cti_displays_dao.get_config()
        return {name: self._format_columns(column)
                for name, column in raw.iteritems()}

    def _format_columns(self, column_configs):
        keys = sorted(column_configs.iterkeys())
        return [self._format_line(column_configs[key]) for key in keys]

    def _format_line(self, line_config):
        default_index = self._fields.index('default')
        line_config[default_index] = line_config[default_index] or None
        return dict(zip(self._fields, line_config))


class _LookupServiceMixin(object):

    _default_sources = ['personal']
    _default_timeout = 2.9

    def __init__(self, profile_configuration):
        self._profile_config = profile_configuration


class _NoContextSeparationLookupServiceGenerator(_LookupServiceMixin):

    def generate(self):
        return {profile: {'sources': conf['sources'] + self._default_sources,
                          'timeout': self._default_timeout}
                for profile, conf in self._profile_config.iteritems()}


class _ContextSeparatedLookupServiceGenerator(_ContextSeparatedMixin, _LookupServiceMixin):

    def generate(self):
        return {profile: {'sources': list(self._generate_sources(profile, conf)),
                          'timeout': self._default_timeout}
                for profile, conf in self._profile_config.iteritems()}

    def _generate_sources(self, profile, profile_config):
        for source, type_ in zip(profile_config['sources'], profile_config['types']):
            yield self.source_name(profile, source, type_)

        for source in self._default_sources:
            yield source


class _NoContextSeparationFavoritesServiceGenerator(_NoContextSeparationLookupServiceGenerator):
    pass


class _ContextSeparatedFavoritesServiceGenerator(_ContextSeparatedLookupServiceGenerator):
    pass


class _ContextSeparatedReverseServiceGenerator(_ContextSeparatedMixin):

    _default_sources = ['personal']
    _default_profile = 'default'
    _default_timeout = 1

    def __init__(self, reverse_configuration):
        self._reverse_config = reverse_configuration

    def generate(self):
        sources = list(self._generate_sources(self._default_profile, self._reverse_config))
        return {self._default_profile: {'sources': sources,
                                        'timeout': self._default_timeout}}

    def _generate_sources(self, profile, config):
        for source, type_ in zip(config['sources'], config['types']):
            yield self.source_name(profile, source, type_)

        for source in self._default_sources:
            yield source


class _NoContextSeparationReverseServiceGenerator(object):

    _default_sources = ['personal']
    _default_profile = 'default'
    _default_timeout = 1

    def __init__(self, reverse_configuration):
        self._reverse_config = reverse_configuration

    def generate(self):
        return {self._default_profile: {'sources': self._reverse_config['sources'] + self._default_sources,
                                        'timeout': self._default_timeout}}


class DirdFrontend(object):

    def __init__(self):
        self._no_context_separation_backend = _NoContextSeparationDirdFrontend()
        self._context_separated_backend = _ContextSeparatedDirdFrontend()

    def __getattr__(self, name):
        if bool(cti_main_dao.get_config()['main']['context_separation']):
            selected_implementation = self._context_separated_backend
        else:
            selected_implementation = self._no_context_separation_backend

        return getattr(selected_implementation, name)


class _BaseDirdFrontend(object):

    def services_yml(self):
        profile_config = cti_displays_dao.get_profile_configuration()
        reverse_config = cti_reverse_dao.get_config()

        lookups = self._LookupServiceGenerator(profile_config).generate()
        favorites = self._FavoritesServiceGenerator(profile_config).generate()
        reverses = self._ReverseServiceGenerator(reverse_config).generate()

        return yaml.safe_dump({'services': {'lookup': lookups,
                                            'favorites': favorites,
                                            'reverse': reverses}})

    def views_yml(self):
        displays = _DisplayGenerator().generate()
        associations = _AssociationGenerator().generate()
        phone_associations = _PhoneAssociationGenerator().generate()

        views_section = {'views': {'displays': displays,
                                   'profile_to_display': associations,
                                   'profile_to_display_phone': phone_associations}}

        return yaml.safe_dump(views_section)


class _ContextSeparatedDirdFrontend(_BaseDirdFrontend):

    _LookupServiceGenerator = _ContextSeparatedLookupServiceGenerator
    _FavoritesServiceGenerator = _ContextSeparatedFavoritesServiceGenerator
    _ReverseServiceGenerator = _ContextSeparatedReverseServiceGenerator


class _NoContextSeparationDirdFrontend(_BaseDirdFrontend):

    _LookupServiceGenerator = _NoContextSeparationLookupServiceGenerator
    _FavoritesServiceGenerator = _NoContextSeparationFavoritesServiceGenerator
    _ReverseServiceGenerator = _NoContextSeparationReverseServiceGenerator
