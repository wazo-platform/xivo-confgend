# -*- coding: utf-8 -*-
# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


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
        if key not in self._cache:
            self._cache[key] = self._factory.get(resource, filename)
        return self._cache[key]


class MultiHandlerFactory(HandlerFactory):
    def __init__(self, factories):
        self._factories = factories

    def get(self, resource, filename):
        for handler_factory in self._factories:
            try:
                return handler_factory.get(resource, filename)
            except NoSuchHandler:
                continue
        raise NoSuchHandler()


class PluginHandlerFactory(HandlerFactory):
    def __init__(self, config, dependencies):
        self._config = config
        self._dependencies = dependencies

    def get(self, resource, filename):
        suffix = '{}.{}'.format(resource, filename)
        namespace = 'wazo_confgend.{}'.format(suffix)
        driver_name = self._config['plugins'].get(suffix)
        if not driver_name:
            raise NoSuchHandler()

        try:
            generator = driver.DriverManager(
                namespace=namespace,
                name=driver_name,
                invoke_on_load=True,
                invoke_args=(self._dependencies,),
            ).driver
        except RuntimeError:
            raise NoSuchHandler()
        else:
            logger.info("Loaded plugin %s for namespace %s", driver_name, namespace)
            return generator.generate


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
