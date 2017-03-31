#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Mon May  4 16:59:45 2015
# ht <515563130@qq.com, weixin:jacoolee>

import tornado.ioloop
import tornado.web

from black_pearl_uom import BlackPearlUOM
from black_pearl_request import BlackPearlRequestHandler

from black_pearl_utils import log

class BlackPearlServer(object):
    def __init__(self, debug=True, port=8888, configure_manager=None, modules=[], handlers=[], **application_settings):
        self.debug = debug
        self.port = port
        self.cm = configure_manager
        self.modules = modules
        self.handlers = handlers
        self.application_settings = application_settings

        self._post_init()

    def before_run(self, *args,**kwargs):
        pass

    def _post_init(self):
        log.info('post initialization ...')
        for i in self.modules:
            BlackPearlUOM.importModule(i)
        module_handers = BlackPearlUOM.load((BlackPearlRequestHandler,))
        self.handlers += module_handers
        self.application_settings['debug'] = self.debug

        log.info(BlackPearlUOM.info())

    def run(self, *args, **kwargs):
        log.info("before running server, do ...")
        self.before_run(*args, **kwargs)

        log.info("running server http://localhost:"+str(self.port))

        if self.debug:
            log.info('handler count: '+str(len(self.handlers)))
            log.info('modules count: '+str(len(self.modules)))
            log.info('app settings:  '+str(self.application_settings))

        # run.
        application = tornado.web.Application( self.handlers, **self.application_settings )
        application.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()
