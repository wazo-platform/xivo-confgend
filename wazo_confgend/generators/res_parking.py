# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.parking_lot import dao as parking_lot_dao

from wazo_confgend.generators.util import AsteriskFileWriter


class ResParkingConf:
    def __init__(self):
        self._parking_lots = parking_lot_dao.find_all_by()

    def generate(self, output):
        ast_file = AsteriskFileWriter(output)
        self._generate_default_parking_lot(ast_file)
        self._generate_parking_lots(ast_file)

    def _generate_default_parking_lot(self, ast_file):
        section = 'default'
        options = [
            ('context', 'wazo-disabled'),
        ]

        ast_file.write_section(section)
        ast_file.write_options(options)

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
