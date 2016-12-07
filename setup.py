#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-confgend',
    version='0.2',
    description='XIVO Configurations Generator',
    author='Avencall',
    author_email='dev+pkg@proformatique.com',
    url='http://www.xivo.io/',
    license='GPLv3',
    include_package_data=True,
    packages=find_packages(),
    scripts=['bin/xivo-confgend'],
    entry_points={
        'xivo_confgend.asterisk.confbridge.conf': [
            'xivo = xivo_confgen.plugins.confbridge_conf:ConfBridgeConfGenerator',
        ],
        'xivo_confgend.asterisk.sip.conf': [
            'xivo = xivo_confgen.plugins.sip_conf:SIPConfGenerator',
        ],
        'xivo_confgend.dird.sources.yml': [
            'xivo = xivo_confgen.plugins.dird_sources:SourceGenerator',
        ],
    },
)
