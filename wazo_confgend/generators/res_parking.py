# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from wazo_confgend.generators.util import AsteriskFileWriter
from xivo_dao import asterisk_conf_dao
from xivo_dao.resources.parking_lot import dao as parking_lot_dao


class ResParkingConf:
    def __init__(self):
        self._settings = asterisk_conf_dao.find_parking_settings()
        self._parking_lots = parking_lot_dao.find_all_by()

    def generate(self, output):
        ast_file = AsteriskFileWriter(output)
        self._generate_general(ast_file)
        self._generate_default_parking_lot(ast_file)
        self._generate_parking_lots(ast_file)

    def _generate_general(self, ast_file):
        ast_file.write_section('general')
        ast_file.write_options(self._settings['general_options'])

    def _generate_default_parking_lot(self, ast_file):
        for parking_lot in self._settings['parking_lots']:
            ast_file.write_section(parking_lot['name'])
            ast_file.write_options(parking_lot['options'])

    def _generate_parking_lots(self, ast_file):
        for parking_lot in self._parking_lots:
            if not parking_lot.extensions:
                continue

            section = f'parkinglot-{parking_lot.id}'
            options = [
                ('parkext', parking_lot.extensions[0].exten),
                ('context', parking_lot.extensions[0].context),
                ('parkedmusicclass', parking_lot.music_on_hold or ''),
                (
                    'parkpos',
                    f'{parking_lot.slots_start}-{parking_lot.slots_end}',
                ),
                ('parkingtime', parking_lot.timeout or 0),
                ('findslot', 'next'),
                ('parkext_exclusive', 'yes'),
                ('parkinghints', 'yes'),
                ('comebacktoorigin', 'yes'),
                ('parkedplay', 'caller'),
                ('parkedcalltransfers', 'no'),
                ('parkedcallreparking', 'no'),
                ('parkedcallhangup', 'no'),
                ('parkedcallrecording', 'no'),
            ]

            ast_file.write_section(section)
            ast_file.write_options(options)
