#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo-confgend',
    version='0.2',
    description='Wazo configurations generator',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo-platform.org',
    license='GPLv3',
    include_package_data=True,
    packages=find_packages(),
    scripts=['bin/wazo-confgend'],
    entry_points={
        'wazo_confgend.asterisk.confbridge.conf': [
            'wazo = wazo_confgend.plugins.confbridge_conf:ConfBridgeConfGenerator',
        ],
        'wazo_confgend.asterisk.hep.conf': [
            'wazo = wazo_confgend.plugins.hep_conf:HEPConfGenerator',
        ],
        'wazo_confgend.asterisk.modules.conf': [
            'wazo = wazo_confgend.plugins.modules_conf:ModulesConfGenerator',
        ],
        'wazo_confgend.asterisk.musiconhold.conf': [
            'wazo = wazo_confgend.plugins.musiconhold_conf:MOHConfGenerator',
        ],
        'wazo_confgend.asterisk.rtp.conf': [
            'wazo = wazo_confgend.plugins.rtp_conf:RTPConfGenerator',
        ],
        'wazo_confgend.asterisk.pjsip.conf': [
            'wazo = wazo_confgend.plugins.pjsip_conf:PJSIPConfGenerator',
        ],
        'wazo_confgend.provd.network.yml': [
            'wazo = wazo_confgend.plugins.provd_conf:ProvdNetworkConfGenerator',
        ],
    },
)
