# -*- coding: utf-8 -*-
# Copyright 2011-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from operator import itemgetter

from xivo_confgen.generators.util import format_ast_section, \
    format_ast_option, format_ast_section_tpl, format_ast_section_using_tpl
from xivo_dao import asterisk_conf_dao

_GUEST_DEVICE_NAME = 'guest'
_GUEST_LINE_NAME = 'guestline'


class SccpConf(object):

    def __init__(self):
        self._sccpgeneralsettings = asterisk_conf_dao.find_sccp_general_settings()
        self._sccpline = asterisk_conf_dao.find_sccp_line_settings()
        self._sccpdevice = asterisk_conf_dao.find_sccp_device_settings()
        self._sccpspeeddial = asterisk_conf_dao.find_sccp_speeddial_settings()

    def generate(self, output):
        splitted_settings = _SplittedGeneralSettings.new_from_dao_general_settings(self._sccpgeneralsettings)

        sccp_general_conf = _SccpGeneralSettingsConf()
        sccp_general_conf.generate(splitted_settings.general_items, output)

        sccp_device_conf = _SccpDeviceConf(self._sccpspeeddial)
        sccp_device_conf.generate(self._sccpdevice, splitted_settings.device_items, output)

        sccp_line_conf = _SccpLineConf()
        sccp_line_conf.generate(self._sccpline, splitted_settings.line_items, output)

        sccp_speeddial_conf = _SccpSpeedDialConf()
        sccp_speeddial_conf.generate(self._sccpspeeddial, output)


class _SplittedGeneralSettings(object):

    _DEVICE_OPTIONS = ['dialtimeout', 'dateformat', 'vmexten', 'keepalive']
    _LINES_OPTIONS = ['context', 'language', 'directmedia', 'tos_audio', 'disallow', 'allow']

    def __init__(self, general_items, device_items, line_items):
        self.general_items = general_items
        self.device_items = device_items
        self.line_items = line_items

    @classmethod
    def new_from_dao_general_settings(cls, sccp_general_settings):
        general_items = []
        device_items = []
        line_items = []

        for item in sccp_general_settings:
            option_name = item['option_name']
            if option_name in cls._DEVICE_OPTIONS:
                device_items.append(item)
            elif option_name in cls._LINES_OPTIONS:
                line_items.append(item)
            else:
                general_items.append(item)

        return cls(general_items, device_items, line_items)


class _SccpGeneralSettingsConf(object):

    def generate(self, general_items, output):
        print >> output, u'[general]'
        for item in general_items:
            print >> output, format_ast_option(item['option_name'], item['option_value'])
        print >> output


class _SccpDeviceConf(object):

    _TPL_NAME = 'xivo_device_tpl'

    def __init__(self, sccpspeeddialdevices):
        self._sccpspeeddialdevices = sorted(
            sccpspeeddialdevices,
            key=itemgetter('fknum'),
        )

    def generate(self, sccpdevice, general_device_items, output):
        self._generate_template(general_device_items, output)
        self._generate_guest_device(output)
        self._generate_devices(sccpdevice, output)

    def _generate_template(self, device_items, output):
        print >> output, format_ast_section_tpl(self._TPL_NAME)
        for item in device_items:
            print >> output, format_ast_option(item['option_name'], item['option_value'])
        print >> output

    def _generate_guest_device(self, output):
        print >> output, format_ast_section_using_tpl(_GUEST_DEVICE_NAME, self._TPL_NAME)
        print >> output, format_ast_option('type', 'device')
        print >> output, format_ast_option('line', _GUEST_LINE_NAME)
        print >> output

    def _generate_devices(self, sccpdevice, output):
        for item in sccpdevice:
            print >> output, format_ast_section_using_tpl(item['name'], self._TPL_NAME)
            print >> output, format_ast_option('type', 'device')
            if item['line']:
                print >> output, format_ast_option('line', item['line'])
            if item['voicemail']:
                print >> output, format_ast_option('voicemail', item['voicemail'])
            self._generate_speeddials(output, item['device'])
            print >> output

    def _generate_speeddials(self, output, device):
        for item in self._sccpspeeddialdevices:
            if item['device'] == device:
                print >> output, format_ast_option('speeddial', '%d-%d' % (item['user_id'], item['fknum']))


class _SccpLineConf(object):

    _TPL_NAME = 'xivo_line_tpl'

    def generate(self, sccplines, general_line_items, output):
        self._generate_template(general_line_items, output)
        self._generate_guest_line(output)
        self._generate_lines(sccplines, output)

    def _generate_template(self, line_items, output):
        print >> output, format_ast_section_tpl(self._TPL_NAME)
        for item in line_items:
            option_name = item['option_name']
            option_value = item['option_value']

            if option_name == 'allow':
                if not option_value:
                    continue
                print >> output, format_ast_option('disallow', 'all')
            elif option_name == 'disallow':
                continue
            elif option_name == 'directmedia':
                option_value = '0' if option_value == 'no' else '1'

            print >> output, format_ast_option(option_name, option_value)
        print >> output

    def _generate_guest_line(self, output):
        print >> output, format_ast_section_using_tpl(_GUEST_LINE_NAME, self._TPL_NAME)
        print >> output, format_ast_option('type', 'line')
        print >> output, format_ast_option('context', 'xivo-initconfig')
        print >> output, format_ast_option('cid_name', 'Autoprov')
        print >> output, format_ast_option('cid_num', 'autoprov')
        print >> output

    def _generate_lines(self, sccplines, output):
        for item in sccplines:
            print >> output, format_ast_section_using_tpl(item['name'], self._TPL_NAME)
            print >> output, format_ast_option('type', 'line')
            print >> output, format_ast_option('cid_name', item['cid_name'])
            print >> output, format_ast_option('cid_num', item['cid_num'])
            print >> output, format_ast_option('setvar', u'XIVO_ORIGINAL_CALLER_ID="{cid_name}" <{cid_num}>'.format(**item))
            print >> output, format_ast_option('setvar', 'XIVO_USERID=%s' % item['user_id'])
            print >> output, format_ast_option('setvar', 'XIVO_USERUUID=%s' % item['uuid'])
            print >> output, format_ast_option('setvar', 'WAZO_TENANT_UUID=%s' % item['tenant_uuid'])
            print >> output, format_ast_option('setvar', 'PICKUPMARK=%(number)s%%%(context)s' % item)
            print >> output, format_ast_option('setvar', 'TRANSFER_CONTEXT=%s' % item['context'])
            print >> output, format_ast_option('setvar', 'WAZO_CHANNEL_DIRECTION=from-wazo')
            if item['language']:
                print >> output, format_ast_option('language', item['language'])
            print >> output, format_ast_option('context', item['context'])
            if 'disallow' in item:
                print >> output, format_ast_option('disallow', item['disallow'])
            if 'allow' in item:
                print >> output, format_ast_option('allow', item['allow'])
            if 'callgroup' in item:
                print >> output, format_ast_option('namedcallgroup', ','.join(str(i) for i in item['callgroup']))
            if 'pickupgroup' in item:
                print >> output, format_ast_option('namedpickupgroup', ','.join(str(i) for i in item['pickupgroup']))
            print >> output


class _SccpSpeedDialConf(object):
    def generate(self, sccpspeeddial, output):
        for item in sccpspeeddial:
            print >> output, format_ast_section('%d-%d' % (item['user_id'], item['fknum']))
            print >> output, format_ast_option('type', 'speeddial')
            print >> output, format_ast_option('extension', item['exten'])
            if item['label']:
                print >> output, format_ast_option('label', item['label'])
            print >> output, format_ast_option('blf', item['supervision'])
            print >> output
