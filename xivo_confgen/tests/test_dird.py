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

from hamcrest import assert_that, equal_to
from mock import patch

from ..dird import DirdFrontend

sources = [
    {'type': 'xivo',
     'name': 'Internal',
     'uri': 'http://localhost:9487',
     'searched_columns': ['firstname', 'lastname'],
     'format_columns': {'number': '{exten}',
                        'mobile': '{mobile_phone_number}'}},
    {'type': 'xivo',
     'name': 'mtl',
     'uri': 'http://montreal.lan.example.com:9487',
     'searched_columns': ['lastname'],
     'format_columns': {'number': '{exten}',
                        'mobile': '{mobile_phone_number}',
                        'name': '{firstname} {lastname}'}},
    {'type': 'phonebook',
     'name': 'xivodir',
     'uri': 'http://localhost/service/ipbx/json.php/private/pbx_services/phonebook',
     'searched_columns': ['firstname', 'lastname', 'company'],
     'format_columns': {'firstname': '{phonebook.firstname}',
                        'lastname': '{phonebook.lastname}',
                        'number': '{phonebooknumber.office.number}'}},
    {'type': 'csv',
     'name': 'mycsv',
     'uri': 'file:///usr/tmp/test.csv',
     'delimiter': '|',
     'searched_columns': ['firstname', 'lastname'],
     'format_columns': {'name': '{firstname} {lastname}'}},
    {'type': 'csv_ws',
     'name': 'my-csv',
     'delimiter': '|',
     'uri': 'http://localhost:5000/ws',
     'searched_columns': ['firstname', 'lastname'],
     'format_columns': {'name': '{firstname} {lastname}'}},
    {'type': 'ldap',
     'name': 'ldapdirectory',
     'ldap_uri': 'ldaps://myldap.example.com:636',
     'ldap_base_dn': 'dc=example,dc=com',
     'ldap_username': 'cn=admin,dc=example,dc=com',
     'ldap_password': '53c8e7',
     'searched_columns': ['cn'],
     'format_columns': {
         'firstname': '{givenName}',
         'lastname': '{sn}',
         'number': '{telephoneNumber}',
     }},
]


class TestDirdFrontend(unittest.TestCase):

    @patch('xivo_confgen.dird.directory_dao')
    def test_sources_yml(self, mock_directory_dao):
        mock_directory_dao.get_all_sources.return_value = sources

        frontend = DirdFrontend()

        result = frontend.sources_yml()

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
                    }
                },
                'mtl': {
                    'type': 'xivo',
                    'name': 'mtl',
                    'unique_column': 'id',
                    'searched_columns': [
                        'lastname',
                    ],
                    'format_columns': {
                        'number': '{exten}',
                        'mobile': '{mobile_phone_number}',
                        'name': '{firstname} {lastname}',
                    },
                    'confd_config': {
                        'https': False,
                        'host': 'montreal.lan.example.com',
                        'port': 9487,
                        'version': '1.1',
                        'timeout': 4,
                    },
                },
                'xivodir': {
                    'type': 'phonebook',
                    'name': 'xivodir',
                    'phonebook_url': 'http://localhost/service/ipbx/json.php/private/pbx_services/phonebook',
                    'searched_columns': ['firstname', 'lastname', 'company'],
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
                    'format_columns': {'name': '{firstname} {lastname}'},
                },
                'my-csv': {
                    'type': 'csv_ws',
                    'name': 'my-csv',
                    'delimiter': '|',
                    'lookup_url': 'http://localhost:5000/ws',
                    'searched_columns': ['firstname', 'lastname'],
                    'format_columns': {'name': '{firstname} {lastname}'},
                },
                'ldapdirectory': {
                    'type': 'ldap',
                    'name': 'ldapdirectory',
                    'ldap_uri': 'ldaps://myldap.example.com:636',
                    'ldap_base_dn': 'dc=example,dc=com',
                    'ldap_username': 'cn=admin,dc=example,dc=com',
                    'ldap_password': '53c8e7',
                    'searched_columns': ['cn'],
                    'format_columns': {
                        'firstname': '{givenName}',
                        'lastname': '{sn}',
                        'number': '{telephoneNumber}'},
                },
            }
        }

        assert_that(yaml.load(result), equal_to(expected))
