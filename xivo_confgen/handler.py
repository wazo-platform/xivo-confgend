# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from stevedore import driver

logger = logging.getLogger(__name__)


class NoSuchHandler(Exception):
    pass


class HandlerFactory(object):
    pass


class CachedHandlerFactoryDecorator(object):
    def __init__(self, decorated_factory):
        self._factory = decorated_factory
        self._cache = {}

    def get(self, resource, filename):
        key = (resource, filename)
        if key in self._cache:
            result = self._cache[key]
        else:
            result = self._factory.get(resource, filename)
            self._cache[key] = result
        return result


class MultiHandlerFactory(HandlerFactory):
    def __init__(self, factories):
        self._factories = factories

    def get(self, resource, filename):
        for handler_factory in self._factories:
            try:
                return handler_factory.get(resource, filename)
            except NoSuchHandler:
                continue
        else:
            raise NoSuchHandler()


class PluginHandlerFactory(HandlerFactory):
    def __init__(self, config):
        self._config = config

    def get(self, resource, filename):
        suffix = '{}.{}'.format(resource, filename)
        namespace = 'xivo_confgend.{}'.format(suffix)
        driver_name = self._config['plugins'].get(suffix)
        if not driver_name:
            raise NoSuchHandler()

        try:
            return driver.DriverManager(
                namespace=namespace,
                name=driver_name,
                invoke_on_load=True,
                invoke_args=(self._config,),
            ).driver.generate
        except RuntimeError:
            raise NoSuchHandler()


class FrontendHandlerFactory(HandlerFactory):
    def __init__(self, frontends):
        self._frontends = frontends

    def get(self, resource, filename):
        callback = filename.replace('.', '_')
        frontend_name = resource
        frontend = self._frontends.get(frontend_name)
        if frontend is None:
            raise NoSuchHandler()

        try:
            return getattr(frontend, callback)
        except AttributeError as e:
            logger.error(e)
            raise NoSuchHandler()


class NullHandlerFactory(HandlerFactory):

    class _NullHandler(object):
        def __init__(self, resource, filename):
            self._error_msg = 'No handler found for {}/{}'.format(resource, filename)

        def generate(self):
            logger.error(self._error_msg)

    def get(self, resource, filename):
        return self._NullHandler(resource, filename).generate
