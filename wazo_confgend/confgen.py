# -*- coding: utf-8 -*-
# Copyright 2011-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import time

from wazo_confgend import cache
from wazo_confgend.asterisk import AsteriskFrontend
from wazo_confgend.wazo import WazoFrontend
from wazo_confgend.phoned import PhonedFrontend
from wazo_confgend.handler import (
    CachedHandlerFactoryDecorator,
    MultiHandlerFactory,
    PluginHandlerFactory,
    FrontendHandlerFactory,
    NullHandlerFactory,
)
from wazo_confgend.template import new_template_helper
from xivo_dao.helpers.db_utils import session_scope
from twisted.internet.protocol import Protocol, ServerFactory

logger = logging.getLogger(__name__)


class Confgen(Protocol):

    def dataReceived(self, data):
        try:
            t1 = time.time()
            line = data.replace('\n', '')

            if ' ' in line:
                cmd, trailing = line.split(' ', 1)
                args = [arg for arg in trailing.split(' ') if arg]
            else:
                cmd, args = line, []

            try:
                resource, filename = cmd.split('/')
            except ValueError:
                logger.error("cannot split %s", data)
                return

            content = self.factory.generate(resource, filename, *args)
            if content:
                self.transport.write(content)
            t2 = time.time()

            logger.info("serving %s in %.3f seconds", data, t2 - t1)
        finally:
            self.transport.loseConnection()


class ConfgendFactory(ServerFactory):

    protocol = Confgen

    def __init__(self, cachedir, config):
        tpl_helper = new_template_helper()
        dependencies = {
            'config': config,
            'tpl_helper': tpl_helper,
        }
        frontends = {
            'asterisk': AsteriskFrontend(config, tpl_helper),
            'phoned': PhonedFrontend(),
            'wazo': WazoFrontend(),
        }
        self._cache = cache.FileCache(cachedir)
        self._handler_factory = MultiHandlerFactory([
            CachedHandlerFactoryDecorator(PluginHandlerFactory(config, dependencies)),
            FrontendHandlerFactory(frontends),
            NullHandlerFactory(),
        ])

    def generate(self, resource, filename, *args):
        cache_key = '{}/{}'.format(resource, filename)
        if 'invalidate' in args:
            self._cache.invalidate(cache_key)
        elif 'cached' in args:
            return (
                self._get_cached_content(cache_key)
                or self._generate_and_cache(cache_key, resource, filename)
            )
        else:
            return (
                self._generate_and_cache(cache_key, resource, filename)
                or self._get_cached_content(cache_key)
            )

    def _generate_and_cache(self, cache_key, resource, filename):
        handler = self._handler_factory.get(resource, filename)
        with session_scope(read_only=True):
            try:
                content = handler()
                return self._encode_and_cache(cache_key, content)
            except Exception:
                logger.error('unexpected error raised by handler', exc_info=True)

    def _get_cached_content(self, cache_key):
        try:
            return self._cache.get(cache_key)
        except AttributeError:
            logger.warning("No cached content for %s", cache_key)

    def _encode_and_cache(self, cache_key, content):
        if not content:
            return

        encoded_content = content.encode('utf-8')
        self._cache.put(cache_key, encoded_content)
        return encoded_content
