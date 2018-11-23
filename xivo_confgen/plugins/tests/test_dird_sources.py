# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    has_key,
    is_not,
)

from ..dird_sources import _NoContextSeparationSourceGenerator


sources = [
    {'type': 'xivo',
     'name': 'Internal',
     'uri': 'https://localhost:9486',
     'auth_host': 'localhost',
     'auth_port': 9497,
     'auth_backend': 'wazo_user',
     'xivo_username': 'foo',
     'xivo_password': 'bar',
     'auth_verify_certificate': True,
     'auth_custom_ca_path': '/usr/share/xivo-certs/server.crt',
     'xivo_verify_certificate': False,
     'xivo_custom_ca_path': None,
     'searched_columns': ['firstname', 'lastname'],
     'first_matched_columns': ['exten'],
     'format_columns': {'number': '{exten}',
                        'mobile': '{mobile_phone_number}'}},
    {'type': 'xivo',
     'name': 'mtl',
     'uri': 'https://montreal.lan.example.com:9486',
     'auth_host': 'montreal.lan.example.com',
     'auth_port': 9497,
     'auth_backend': 'xivo_service',
     'xivo_username': 'test',
     'xivo_password': 'test',
     'auth_verify_certificate': True,
     'auth_custom_ca_path': None,
     'xivo_verify_certificate': True,
     'xivo_custom_ca_path': None,
     'searched_columns': ['lastname'],
     'first_matched_columns': ['exten'],
     'format_columns': {'number': '{exten}',
                        'mobile': '{mobile_phone_number}',
                        'name': '{firstname} {lastname}'}},
    {'type': 'csv',
     'name': 'mycsv',
     'uri': 'file:///usr/tmp/test.csv',
     'delimiter': '|',
     'searched_columns': ['firstname', 'lastname'],
     'first_matched_columns': [],
     'format_columns': {'name': '{firstname} {lastname}'}},
    {'type': 'csv_ws',
     'name': 'my_csv',
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

        assert_that(
            result,
            has_entries(
                Internal=has_entries(
                    type='xivo',
                    auth={
                        'host': 'localhost',
                        'port': 9497,
                        'username': 'foo',
                        'password': 'bar',
                        'backend': 'wazo_user',
                        'verify_certificate': '/usr/share/xivo-certs/server.crt',
                    },
                    confd={
                        'https': True,
                        'host': 'localhost',
                        'port': 9486,
                        'version': '1.1',
                        'timeout': 4,
                        'verify_certificate': False,
                    }
                ),
                mtl=has_entries(
                    type='xivo',
                    auth={
                        'host': 'montreal.lan.example.com',
                        'port': 9497,
                        'backend': 'xivo_service',
                        'username': 'test',
                        'password': 'test',
                        'verify_certificate': True,
                    },
                    confd={
                        'https': True,
                        'host': 'montreal.lan.example.com',
                        'port': 9486,
                        'version': '1.1',
                        'timeout': 4,
                        'verify_certificate': True,
                    },
                ),
                mycsv=has_entries(
                    type='csv',
                    name='mycsv',
                    separator='|',
                    file='/usr/tmp/test.csv',
                    searched_columns=['firstname', 'lastname'],
                    first_matched_columns=[],
                    format_columns={'name': '{firstname} {lastname}'},
                ),
                my_csv=has_entries(
                    type='csv_ws',
                    lookup_url='http://localhost:5000/ws',
                ),
                ldapdirectory=has_entries(
                    type='ldap',
                    ldap_uri='ldaps://myldap.example.com:636',
                    ldap_base_dn='dc=example,dc=com',
                    ldap_username='cn=admin,dc=example,dc=com',
                    ldap_password='53c8e7',
                    ldap_custom_filter='(st=USA)',
                ),
                dird=has_entries(
                    type='dird_phonebook',
                    name='dird',
                    db_uri='postgresql://db',
                    tenant='tenant',
                    phonebook_name='phonebook-name',
                ),
            )
        )

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
