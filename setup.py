#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-confgend',
    version='0.2',
    description='Wazo configurations generator',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    license='GPLv3',
    include_package_data=True,
    packages=find_packages(),
    scripts=['bin/xivo-confgend'],
    entry_points={
        'xivo_confgend.asterisk.confbridge.conf': [
            'xivo = xivo_confgen.plugins.confbridge_conf:ConfBridgeConfGenerator',
        ],
        'xivo_confgend.asterisk.musiconhold.conf': [
            'xivo = xivo_confgen.plugins.musiconhold_conf:MOHConfGenerator',
        ],
        'xivo_confgend.asterisk.rtp.conf': [
            'xivo = xivo_confgen.plugins.rtp_conf:RTPConfGenerator',
        ],
        'xivo_confgend.asterisk.sip.conf': [
            'xivo = xivo_confgen.plugins.sip_conf:SIPConfGenerator',
        ],
        'xivo_confgend.dird.sources.yml': [
            'xivo = xivo_confgen.plugins.dird_sources:SourceGenerator',
        ],
        'xivo_confgend.asterisk.pjsip.conf': [
            'wazo = xivo_confgen.plugins.pjsip_conf:PJSIPConfGenerator',
        ],
    },
)
