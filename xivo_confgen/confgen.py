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

import logging
import time

from xivo_confgen import cache
from xivo_confgen.asterisk import AsteriskFrontend
from xivo_confgen.xivo import XivoFrontend
from xivo_confgen.dird import DirdFrontend
from xivo_confgen.dird_phoned import DirdPhonedFrontend
from xivo_confgen.handler import CachedHandlerFactoryDecorator
from xivo_confgen.handler import MultiHandlerFactory
from xivo_confgen.handler import PluginHandlerFactory
from xivo_confgen.handler import FrontendHandlerFactory
from xivo_confgen.handler import NullHandlerFactory
from xivo_dao.helpers.db_utils import session_scope
from twisted.internet.protocol import Protocol, ServerFactory

logger = logging.getLogger(__name__)


class Confgen(Protocol):

    def dataReceived(self, data):
        try:
            t1 = time.time()
            try:
                resource, filename = data.replace('\n', '').split('/')
            except ValueError:
                logger.error("cannot split %s", data)
                return

            content = self.factory.generate(resource, filename)
            if content:
                self.transport.write(content)
            t2 = time.time()

            logger.info("serving %s in %.3f seconds", data, t2 - t1)
        finally:
            self.transport.loseConnection()


class ConfgendFactory(ServerFactory):

    protocol = Confgen

    def __init__(self, cachedir, config):
        frontends = {
            'asterisk': AsteriskFrontend(config),
            'dird': DirdFrontend(),
            'dird-phoned': DirdPhonedFrontend(),
            'xivo': XivoFrontend(),
        }
        self._cache = cache.FileCache(cachedir)
        self._handler_factory = CachedHandlerFactoryDecorator(MultiHandlerFactory([PluginHandlerFactory(config),
                                                                                   FrontendHandlerFactory(frontends),
                                                                                   NullHandlerFactory()]))

    def generate(self, resource, filename):
        cache_key = '{}/{}'.format(resource, filename)
        handler = self._handler_factory.get(resource, filename)
        with session_scope():
            try:
                content = handler()
            except Exception:
                logger.error('unexpected error raised by handler', exc_info=True)
                content = self._get_cached_content(cache_key)
        return self._encode_and_cache(cache_key, content)

    def _get_cached_content(self, cache_key):
        logger.info("cache hit on %s", cache_key)
        try:
            return self._cache.get(cache_key).decode('utf-8')
        except AttributeError:
            logger.warning("No cached content for %s", cache_key)

    def _encode_and_cache(self, cache_key, content):
        if not content:
            return

        encoded_content = content.encode('utf-8')
        self._cache.put(cache_key, encoded_content)
        return encoded_content
