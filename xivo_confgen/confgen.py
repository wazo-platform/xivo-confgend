# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016 Avencall
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

import time
import sys

from stevedore import driver, exception

from xivo_confgen import cache
from xivo_confgen.asterisk import AsteriskFrontend
from xivo_confgen.xivo import XivoFrontend
from xivo_confgen.dird import DirdFrontend
from xivo_confgen.dird_phoned import DirdPhonedFrontend
from xivo_dao.helpers.db_utils import session_scope
from twisted.internet.protocol import Protocol, ServerFactory


class Confgen(Protocol):

    def dataReceived(self, data):
        try:
            t1 = time.time()
            try:
                resource, filename = data.replace('\n', '').split('/')
            except ValueError:
                print "cannot split {}".format(data)
                return

            content = self.factory.generate(resource, filename)
            if content:
                self.transport.write(content)
            t2 = time.time()

            print "serving %s in %.3f seconds" % (data, t2 - t1)
        finally:
            self.transport.loseConnection()


class ConfgendFactory(ServerFactory):

    protocol = Confgen

    def __init__(self, cachedir, config):
        self.frontends = {
            'asterisk': AsteriskFrontend(config),
            'dird': DirdFrontend(),
            'dird-phoned': DirdPhonedFrontend(),
            'xivo': XivoFrontend(),
        }
        self._cache = cache.FileCache(cachedir)
        self._handlers = {}
        self._config = config

    def generate(self, resource, filename):
        cache_key = '{}/{}'.format(resource, filename)
        handler = self._get_handler(resource, filename)
        with session_scope():
            content = handler() or self._get_cached_content(cache_key)
        return self._encode_and_cache(cache_key, content)

    def _get_cached_content(self, cache_key):
        print "cache hit on {}".format(cache_key)
        try:
            return self._cache.get(cache_key).decode('utf-8')
        except AttributeError:
            print "No cached content for {}".format(cache_key)

    def _get_handler(self, resource, filename):
        handler_key = '{}.{}'.format(resource, filename)
        if handler_key not in self._handlers:
            self._find_and_update_handler(handler_key, resource, filename)
        return self._handlers[handler_key]

    def _find_and_update_handler(self, handler_key, resource, filename):
        plugin = self._find_plugin(resource, filename)
        if plugin:
            self._handlers[handler_key] = plugin.generate
            return

        frontend_callback = self._find_frontend_callback(resource, filename)
        if frontend_callback:
            self._handlers[handler_key] = frontend_callback
            return

        self._handlers[handler_key] = _NullHandler(resource, filename).generate

    def _find_plugin(self, resource, filename):
        suffix = '{}.{}'.format(resource, filename)
        namespace = 'confgend.{}'.format(suffix)
        driver_name = self._config['plugins'].get(suffix)
        if not driver_name:
            return None

        try:
            return driver.DriverManager(
                namespace=namespace,
                name=driver_name,
                invoke_on_load=True,
                invoke_args=(self._config,),
            ).driver
        except exception.NoMatches:
            return

    def _find_frontend_callback(self, frontend_name, filename):
        callback = filename.replace('.', '_')
        frontend = self.frontends.get(frontend_name)
        if frontend is None:
            return

        try:
            return getattr(frontend, callback)
        except Exception as e:
            import traceback
            print e
            traceback.print_exc(file=sys.stdout)

    def _encode_and_cache(self, cache_key, content):
        if not content:
            return

        encoded_content = content.encode('utf-8')
        self._cache.put(cache_key, encoded_content)
        return encoded_content


class _NullHandler(object):

    def __init__(self, resource, filename):
        self._error_msg = 'No handler found for {}/{}'.format(resource, filename)

    def generate(self):
        print self._error_msg
