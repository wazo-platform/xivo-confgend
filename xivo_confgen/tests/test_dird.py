# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import yaml

from hamcrest import assert_that, equal_to
from mock import DEFAULT, Mock, patch

from ..dird import (_NoContextSeparationDirdFrontend,
                    _AssociationGenerator,
                    _PhoneAssociationGenerator,
                    _DisplayGenerator,
                    _NoContextSeparationLookupServiceGenerator,
                    _ContextSeparatedLookupServiceGenerator,
                    _ContextSeparatedReverseServiceGenerator,
                    _NoContextSeparationReverseServiceGenerator)

LOOKUP_TIMEOUT = _NoContextSeparationLookupServiceGenerator._default_timeout


class TestDirdFrontEndViews(unittest.TestCase):

    @patch('xivo_confgen.dird._AssociationGenerator')
    @patch('xivo_confgen.dird._PhoneAssociationGenerator')
    @patch('xivo_confgen.dird._DisplayGenerator')
    def test_views_yml(self, _DisplayGenerator, _PhoneAssociationGenerator, _AssociationGenerator):
        _AssociationGenerator.return_value.generate.return_value = 'associations'
        _PhoneAssociationGenerator.return_value.generate.return_value = 'phone_associations'
        _DisplayGenerator.return_value.generate.return_value = 'displays'

        frontend = _NoContextSeparationDirdFrontend()

        result = frontend.views_yml()

        expected = {'views': {'displays': 'displays',
                              'profile_to_display': 'associations',
                              'profile_to_display_phone': 'phone_associations'}}

        assert_that(yaml.load(result), equal_to(expected))


class TestNoContextSeparationDirdFrontendViewsGenerators(unittest.TestCase):

    @patch('xivo_confgen.dird.cti_displays_dao')
    def test_display_generator(self, mock_cti_displays_dao):
        mock_cti_displays_dao.get_config.return_value = {
            'mydisplay': {
                '10': ['Firstname', 'name', '', 'firstname'],
                '20': ['Lastname', '', '', 'lastname'],
                '30': ['Number', 'number', '', 'number'],
                '110': ['Favorite', 'favorite', '', 'favorite'],
            },
            'second': {
                '10': ['Nom', 'name', 'Unknown', 'name'],
                '20': ['Numéro', 'number', '', 'exten'],
            }}

        display_generator = _DisplayGenerator()

        result = display_generator.generate()

        expected = {
            'mydisplay': [{'title': 'Firstname', 'field': 'firstname', 'type': 'name', 'default': None},
                          {'title': 'Lastname', 'field': 'lastname', 'type': '', 'default': None},
                          {'title': 'Number', 'field': 'number', 'type': 'number', 'default': None},
                          {'title': 'Favorite', 'field': 'favorite', 'type': 'favorite', 'default': None}],
            'second': [{'title': 'Nom', 'field': 'name', 'type': 'name', 'default': 'Unknown'},
                       {'title': 'Numéro', 'field': 'exten', 'type': 'number', 'default': None}],
        }

        assert_that(result, equal_to(expected))

    @patch('xivo_confgen.dird.cti_displays_dao')
    def test_profile_association_generator(self, mock_cti_displays_dao):
        mock_cti_displays_dao.get_profile_configuration.return_value = {
            'default': {'display': 'mydisplay'},
            'switchboard': {'display': 'sb-display'},
        }
        association_generator = _AssociationGenerator()

        result = association_generator.generate()

        expected = {'default': 'mydisplay',
                    'switchboard': 'sb-display'}

        assert_that(result, equal_to(expected))

    @patch('xivo_confgen.dird.cti_context_dao')
    def test_phone_profile_association_generator(self, mock_cti_context_dao):
        mock_cti_context_dao.get_context_names.return_value = [
            'foo',
            'bar',
        ]
        phone_association_generator = _PhoneAssociationGenerator()

        result = phone_association_generator.generate()

        expected = {'foo': _PhoneAssociationGenerator._DEFAULT_PHONE_DISPLAY,
                    'bar': _PhoneAssociationGenerator._DEFAULT_PHONE_DISPLAY}

        assert_that(result, equal_to(expected))


class TestNoContextSeparationLookupServiceGenerator(unittest.TestCase):

    def test_generate(self):
        profile_configuration = {'switchboard': {'sources': ['my-xivo', 'ldapone']},
                                 'internal': {'sources': ['ldapone', 'ldaptwo']}}

        generator = _NoContextSeparationLookupServiceGenerator(profile_configuration)

        result = generator.generate()

        expected = {'switchboard': {'sources': {'my-xivo': True, 'ldapone': True, 'personal': True},
                                    'timeout': LOOKUP_TIMEOUT},
                    'internal': {'sources': {'ldapone': True, 'ldaptwo': True, 'personal': True},
                                 'timeout': LOOKUP_TIMEOUT}}

        assert_that(result, equal_to(expected))


class TestContextSeparatedLookupServiceGenerator(unittest.TestCase):

    def test_generate(self):
        profile_configuration = {'switchboard': {'sources': ['my-xivo', 'ldapone'],
                                                 'types': ['xivo', 'ldap']},
                                 'internal': {'sources': ['ldapone', 'ldaptwo'],
                                              'types': ['ldap', 'ldap']},
                                 'default': {'sources': ['ldapone', 'my-xivo'],
                                             'types': ['ldap', 'xivo']}}

        generator = _ContextSeparatedLookupServiceGenerator(profile_configuration)

        result = generator.generate()

        expected = {'switchboard': {'sources': {'my-xivo_switchboard': True, 'ldapone': True, 'personal': True},
                                    'timeout': LOOKUP_TIMEOUT},
                    'internal': {'sources': {'ldapone': True, 'ldaptwo': True, 'personal': True},
                                 'timeout': LOOKUP_TIMEOUT},
                    'default': {'sources': {'ldapone': True, 'my-xivo_default': True, 'personal': True},
                                'timeout': LOOKUP_TIMEOUT}}

        assert_that(result, equal_to(expected))


class TestNoContextSeparatReverseServiceGenerator(unittest.TestCase):

    def test_generate(self):
        reverse_configuration = {'sources': ['internal', 'xivodir'],
                                 'types': ['dird_phonebook', 'xivo']}

        generator = _NoContextSeparationReverseServiceGenerator(reverse_configuration)

        result = generator.generate()

        expected = {'default': {'sources': {'internal': True, 'xivodir': True, 'personal': True},
                                'timeout': 1}}

        assert_that(result, equal_to(expected))


class TestContextSeparatedReverseServiceGenerator(unittest.TestCase):

    def test_generate(self):
        reverse_configuration = {'sources': ['internal', 'xivodir'],
                                 'types': ['dird_phonebook', 'xivo']}

        generator = _ContextSeparatedReverseServiceGenerator(reverse_configuration)

        result = generator.generate()

        expected = {'default': {'sources': {'internal': True, 'xivodir_default': True, 'personal': True},
                                'timeout': 1}}

        assert_that(result, equal_to(expected))


class TestNoContextSeparationDirdFrontendServices(unittest.TestCase):

    @patch('xivo_confgen.dird.cti_displays_dao', Mock())
    @patch('xivo_confgen.dird.cti_reverse_dao', Mock())
    def test_services_yml(self):
        frontend = _NoContextSeparationDirdFrontend()
        with patch.multiple(frontend,
                            _LookupServiceGenerator=DEFAULT,
                            _FavoritesServiceGenerator=DEFAULT,
                            _ReverseServiceGenerator=DEFAULT) as Factories:
            Factories['_LookupServiceGenerator'].return_value.generate.return_value = 'lookups'
            Factories['_FavoritesServiceGenerator'].return_value.generate.return_value = 'favorites'
            Factories['_ReverseServiceGenerator'].return_value.generate.return_value = 'reverses'

            result = frontend.services_yml()

        expected = {'services': {'lookup': 'lookups',
                                 'favorites': 'favorites',
                                 'reverse': 'reverses'}}

        assert_that(yaml.load(result), equal_to(expected))
