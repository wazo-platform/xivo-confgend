#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-confgend',
    version='0.2',
    description='XIVO Configurations Generator',
    author='Avencall',
    author_email='xivo-dev@lists.proformatique.com',
    url='http://www.xivo.io/',
    license='GPLv3',
    packages=find_packages(),
    scripts=['bin/xivo-confgend'],
)
