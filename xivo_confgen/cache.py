# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import os.path


class Cache(object):
    def get(self, key):
        raise NotImplementedError()

    def put(self, key, value):
        raise NotImplementedError()


class FileCache(Cache):
    def __init__(self, basedir):
        super(FileCache, self).__init__()
        self.basedir = basedir

    def get(self, key):
        path = self._get_path_from_key(key)
        if not os.path.exists(path):
            return None
        with open(path) as f:
            content = f.read()
        return content

    def _get_path_from_key(self, key):
        return os.path.join(self.basedir, key)

    def put(self, key, value):
        path = self._get_path_from_key(key)
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
            except Exception:
                return False
        with open(path, 'w') as f:
            f.write(value)
        return True
