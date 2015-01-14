#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages
import fnmatch
import os


setup(
    name='xivo-confgen',
    version='0.1',
    description='XIVO Configurations Generator',
    author='Avencall',
    author_email='xivo-dev@lists.proformatique.com',
    url='http://wiki.xivo.io/',
    license='GPLv3',
    packages=find_packages(),
    scripts=['bin/xivo-confgen', 'bin/xivo-confgend'],
    data_files=[('/etc/xivo', ['etc/xivo-confgen.conf', 'etc/xivo-confgend.conf']),
                ('/etc/xivo/xivo-confgend/asterisk', ['etc/asterisk/contexts.conf'])],
)
