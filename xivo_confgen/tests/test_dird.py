# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

import unittest
import yaml

from hamcrest import assert_that, equal_to, has_key, is_not
from mock import Mock, patch

from ..dird import (DirdFrontend,
                    _AssociationGenerator,
                    _PhoneAssociationGenerator,
                    _DisplayGenerator,
                    _LookupServiceGenerator,
                    _ReverseServiceGenerator)

sources = [
    {'type': 'xivo',
     'name': 'Internal',
     'uri': 'http://localhost:9487',
     'xivo_username': None,
     'xivo_password': None,
     'xivo_verify_certificate': False,
     'xivo_custom_ca_path': None,
     'searched_columns': ['firstname', 'lastname'],
     'first_matched_columns': ['exten'],
     'format_columns': {'number': '{exten}',
                        'mobile': '{mobile_phone_number}'}},
    {'type': 'xivo',
     'name': 'mtl',
     'uri': 'https://montreal.lan.example.com:9487',
     'xivo_username': 'foo',
     'xivo_password': 'passwd',
     'xivo_verify_certificate': True,
     'xivo_custom_ca_path': '/tmp/ca.crt',
     'searched_columns': ['lastname'],
     'first_matched_columns': ['exten'],
     'format_columns': {'number': '{exten}',
                        'mobile': '{mobile_phone_number}',
                        'name': '{firstname} {lastname}'}},
    {'type': 'phonebook',
     'name': 'xivodir',
     'uri': 'http://localhost/service/ipbx/json.php/private/pbx_services/phonebook',
     'searched_columns': ['firstname', 'lastname', 'company'],
     'first_matched_columns': ['number'],
     'format_columns': {'firstname': '{phonebook.firstname}',
                        'lastname': '{phonebook.lastname}',
                        'number': '{phonebooknumber.office.number}'}},
    {'type': 'csv',
     'name': 'mycsv',
     'uri': 'file:///usr/tmp/test.csv',
     'delimiter': '|',
     'searched_columns': ['firstname', 'lastname'],
     'first_matched_columns': [],
     'format_columns': {'name': '{firstname} {lastname}'}},
    {'type': 'csv_ws',
     'name': 'my-csv',
     'delimiter': '|',
     'uri': 'http://localhost:5000/ws',
     'searched_columns': ['firstname', 'lastname'],
     'first_matched_columns': [],
     'format_columns': {'name': '{firstname} {lastname}'}},
    {'type': 'ldap',
     'name': 'ldapdirectory',
     'ldap_uri': 'ldaps://myldap.example.com:636',
     'ldap_base_dn': 'dc=example,dc=com',
     'ldap_username': 'cn=admin,dc=example,dc=com',
     'ldap_password': '53c8e7',
     'ldap_custom_filter': '(st=USA)',
     'searched_columns': ['cn'],
     'first_matched_columns': ['telephoneNumber'],
     'format_columns': {
         'firstname': '{givenName}',
         'lastname': '{sn}',
         'number': '{telephoneNumber}',
     }},
]


class TestDirdFrontendSources(unittest.TestCase):

    def setUp(self):
        self.frontend = DirdFrontend()

    @patch('xivo_confgen.dird.directory_dao')
    def test_sources_yml(self, mock_directory_dao):
        mock_directory_dao.get_all_sources.return_value = sources

        result = self.frontend.sources_yml()

        expected = {
            'sources': {
                'Internal': {
                    'type': 'xivo',
                    'name': 'Internal',
                    'unique_column': 'id',
                    'searched_columns': [
                        'firstname',
                        'lastname',
                    ],
                    'first_matched_columns': ['exten'],
                    'format_columns': {
                        'number': '{exten}',
                        'mobile': '{mobile_phone_number}',
                    },
                    'confd_config': {
                        'https': False,
                        'host': 'localhost',
                        'port': 9487,
                        'version': '1.1',
                        'timeout': 4,
                        'verify_certificate': False,
                    }
                },
                'mtl': {
                    'type': 'xivo',
                    'name': 'mtl',
                    'unique_column': 'id',
                    'searched_columns': [
                        'lastname',
                    ],
                    'first_matched_columns': ['exten'],
                    'format_columns': {
                        'number': '{exten}',
                        'mobile': '{mobile_phone_number}',
                        'name': '{firstname} {lastname}',
                    },
                    'confd_config': {
                        'https': True,
                        'host': 'montreal.lan.example.com',
                        'port': 9487,
                        'version': '1.1',
                        'timeout': 4,
                        'username': 'foo',
                        'password': 'passwd',
                        'verify_certificate': '/tmp/ca.crt',
                    },
                },
                'xivodir': {
                    'type': 'phonebook',
                    'name': 'xivodir',
                    'phonebook_url': 'http://localhost/service/ipbx/json.php/private/pbx_services/phonebook',
                    'searched_columns': ['firstname', 'lastname', 'company'],
                    'first_matched_columns': ['number'],
                    'format_columns': {'firstname': '{phonebook.firstname}',
                                       'lastname': '{phonebook.lastname}',
                                       'number': '{phonebooknumber.office.number}'},
                    'phonebook_timeout': 4,
                },
                'mycsv': {
                    'type': 'csv',
                    'name': 'mycsv',
                    'separator': '|',
                    'file': '/usr/tmp/test.csv',
                    'searched_columns': ['firstname', 'lastname'],
                    'first_matched_columns': [],
                    'format_columns': {'name': '{firstname} {lastname}'},
                },
                'my-csv': {
                    'type': 'csv_ws',
                    'name': 'my-csv',
                    'delimiter': '|',
                    'lookup_url': 'http://localhost:5000/ws',
                    'searched_columns': ['firstname', 'lastname'],
                    'first_matched_columns': [],
                    'format_columns': {'name': '{firstname} {lastname}'},
                },
                'ldapdirectory': {
                    'type': 'ldap',
                    'name': 'ldapdirectory',
                    'ldap_uri': 'ldaps://myldap.example.com:636',
                    'ldap_base_dn': 'dc=example,dc=com',
                    'ldap_username': 'cn=admin,dc=example,dc=com',
                    'ldap_password': '53c8e7',
                    'ldap_custom_filter': '(st=USA)',
                    'searched_columns': ['cn'],
                    'first_matched_columns': ['telephoneNumber'],
                    'format_columns': {
                        'firstname': '{givenName}',
                        'lastname': '{sn}',
                        'number': '{telephoneNumber}'},
                },
            }
        }

        assert_that(yaml.load(result), equal_to(expected))

    def test_format_confd_allow_unspecified_port(self):
        source = {
            'uri': 'http://169.254.1.1',
            'xivo_username': None,
            'xivo_password': None,
            'xivo_verify_certificate': False,
        }

        config = self.frontend._format_confd_config(source)

        assert_that(config, is_not(has_key('port')))

    def test_format_confd_verify_yes(self):
        source = {
            'xivo_verify_certificate': True,
            'xivo_custom_ca_path': None,
        }

        assert_that(self.frontend._format_confd_verify_certificate(source), equal_to(True))

    def test_format_confd_verify_no(self):
        source = {
            'xivo_verify_certificate': False,
        }

        assert_that(self.frontend._format_confd_verify_certificate(source), equal_to(False))

    def test_format_confd_verify_custom(self):
        source = {
            'xivo_verify_certificate': True,
            'xivo_custom_ca_path': '/tmp/s.crt',
        }

        assert_that(self.frontend._format_confd_verify_certificate(source), equal_to('/tmp/s.crt'))


class TestDirdFrontEndViews(unittest.TestCase):

    @patch('xivo_confgen.dird._AssociationGenerator')
    @patch('xivo_confgen.dird._PhoneAssociationGenerator')
    @patch('xivo_confgen.dird._DisplayGenerator')
    def test_views_yml(self, _DisplayGenerator, _PhoneAssociationGenerator, _AssociationGenerator):
        _AssociationGenerator.return_value.generate.return_value = 'associations'
        _PhoneAssociationGenerator.return_value.generate.return_value = 'phone_associations'
        _DisplayGenerator.return_value.generate.return_value = 'displays'

        frontend = DirdFrontend()

        result = frontend.views_yml()

        expected = {'views': {'displays': 'displays',
                              'profile_to_display': 'associations',
                              'profile_to_display_phone': 'phone_associations'}}

        assert_that(yaml.load(result), equal_to(expected))


class TestDirdFrontendViewsGenerators(unittest.TestCase):

    @patch('xivo_confgen.dird.cti_displays_dao')
    def test_display_generator(self, mock_cti_displays_dao):
        mock_cti_displays_dao.get_config.return_value = {
            'mydisplay': {
                '10': ['Firstname', 'name', '', 'firstname'],
                '20': ['Lastname', '', '', 'lastname'],
                '30': ['Number', 'number', '', 'number'],
                '40': ['Favorite', 'favorite', '', 'favorite'],
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


class TestLookupServiceGenerator(unittest.TestCase):

    def test_generate(self):
        profile_configuration = {'switchboard': {'sources': ['my-xivo', 'ldapone']},
                                 'internal': {'sources': ['ldapone', 'ldaptwo']}}

        generator = _LookupServiceGenerator(profile_configuration)

        result = generator.generate()

        expected = {'switchboard': {'sources': ['my-xivo', 'ldapone', 'personal']},
                    'internal': {'sources': ['ldapone', 'ldaptwo', 'personal']}}

        assert_that(result, equal_to(expected))


class TestServiceServiceGenerator(unittest.TestCase):

    def test_generate(self):
        reverse_configuration = ['internal', 'xivodir']

        generator = _ReverseServiceGenerator(reverse_configuration)

        result = generator.generate()

        expected = {'default': {'sources': ['internal', 'xivodir', 'personal'],
                                'timeout': 1}}

        assert_that(result, equal_to(expected))


class TestDirdFrontendServices(unittest.TestCase):

    @patch('xivo_confgen.dird.cti_displays_dao', Mock())
    @patch('xivo_confgen.dird.cti_reverse_dao', Mock())
    @patch('xivo_confgen.dird._ReverseServiceGenerator')
    @patch('xivo_confgen.dird._LookupServiceGenerator')
    @patch('xivo_confgen.dird._FavoritesServiceGenerator')
    def test_services_yml(self, _FavoritesServiceGenerator, _LookupServiceGenerator, _ReverseServiceGenerator):
        _LookupServiceGenerator.return_value.generate.return_value = 'lookups'
        _FavoritesServiceGenerator.return_value.generate.return_value = 'favorites'
        _ReverseServiceGenerator.return_value.generate.return_value = 'reverses'

        frontend = DirdFrontend()

        result = frontend.services_yml()

        expected = {'services': {'lookup': 'lookups',
                                 'favorites': 'favorites',
                                 'reverse': 'reverses'}}

        assert_that(yaml.load(result), equal_to(expected))
