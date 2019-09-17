# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import xivo_dao

from twisted.application import service, internet
from twisted.internet import reactor
from twisted.python import log
from xivo import xivo_logging
from wazo_confgend.confgen import ConfgendFactory
from wazo_confgend.config import load as load_config


def main():
    config = load_config()

    foreground = True
    xivo_logging.setup_logging(config['log_filename'], foreground, config['debug'], config['log_level'])

    xivo_dao.init_db(config['db_uri'])
    f = ConfgendFactory(config['cache'], config)

    reactor.listenTCP(config['listen_port'], f, interface=config['listen_address'])
    reactor.run()


def twisted_application():
    config = load_config()

    foreground = False
    xivo_logging.setup_logging(config['log_filename'], foreground, config['debug'], config['log_level'])

    xivo_dao.init_db(config['db_uri'])
    f = ConfgendFactory(config['cache'], config)

    application = service.Application('confgend')

    svc = internet.TCPServer(config['listen_port'], f, interface=config['listen_address'])
    svc.setServiceParent(application)

    return application


# given in command line to redirect logs to standard logging
def twistd_logs():
    return log.PythonLoggingObserver().emit
