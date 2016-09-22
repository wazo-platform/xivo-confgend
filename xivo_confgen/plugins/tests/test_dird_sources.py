# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from hamcrest import assert_that, equal_to, has_key, is_not

from ..dird_sources import _NoContextSeparationSourceGenerator


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
         'number': '{telephoneNumber}'}},
    {'type': 'dird_phonebook',
     'uri': 'postgresql://db',
     'dird_tenant': 'tenant',
     'dird_phonebook': 'phonebook-name',
     'name': 'dird',
     'searched_columns': [],
     'first_matched_columns': [],
     'format_columns': {}},
]


class TestNoContextSeparationSourceGenerator(unittest.TestCase):

    def test_sources_yml(self):
        generator = _NoContextSeparationSourceGenerator(sources)

        result = generator.generate()

        expected = {
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
            'dird': {
                'type': 'dird_phonebook',
                'name': 'dird',
                'db_uri': 'postgresql://db',
                'tenant': 'tenant',
                'phonebook_name': 'phonebook-name',
                'format_columns': {},
                'searched_columns': [],
                'first_matched_columns': [],
            },
        }

        assert_that(result, equal_to(expected))

    def test_format_confd_allow_unspecified_port(self):
        source = {
            'uri': 'http://169.254.1.1',
            'xivo_username': None,
            'xivo_password': None,
            'xivo_verify_certificate': False,
        }

        generator = _NoContextSeparationSourceGenerator(source)
        config = generator._format_confd_config(source)

        assert_that(config, is_not(has_key('port')))

    def test_format_confd_verify_yes(self):
        source = {
            'xivo_verify_certificate': True,
            'xivo_custom_ca_path': None,
        }

        generator = _NoContextSeparationSourceGenerator(source)
        assert_that(generator._format_confd_verify_certificate(source), equal_to(True))

    def test_format_confd_verify_no(self):
        source = {
            'xivo_verify_certificate': False,
        }

        generator = _NoContextSeparationSourceGenerator(source)
        assert_that(generator._format_confd_verify_certificate(source), equal_to(False))

    def test_format_confd_verify_custom(self):
        source = {
            'xivo_verify_certificate': True,
            'xivo_custom_ca_path': '/tmp/s.crt',
        }

        generator = _NoContextSeparationSourceGenerator(source)
        assert_that(generator._format_confd_verify_certificate(source), equal_to('/tmp/s.crt'))
