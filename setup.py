#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    packages=find_packages(),
    scripts=['bin/xivo-confgend'],
    entry_points={
        'xivo_confgend.asterisk.sip.conf': [
            'xivo = xivo_confgen.plugins.sip_conf:SIPConfGenerator',
        ],
        'xivo_confgend.dird.sources.yml': [
            'xivo = xivo_confgen.plugins.dird_sources:SourceGenerator',
        ],
    },
)
