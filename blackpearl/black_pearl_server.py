#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Mon May  4 16:59:45 2015
# ht <515563130@qq.com, weixin:jacoolee>

import tornado.ioloop
import tornado.web

from logger.logger import Logger

from black_pearl_uom import BlackPearlUOM
from black_pearl_request import BlackPearlRequestHandler

from black_pearl_trace import BlackPearlTrace

logger = Logger('BLACK_PEARL_SERVER')

class BlackPearlServer(object):
    def __init__(self, service_name='BlackPearlServer', debug=True, port=8888, configure_manager=None, modules=[], handlers=[], **application_settings):
        self.debug = debug
        self.port = port
        self.cm = configure_manager
        self.modules = modules
        self.handlers = handlers
        self.application_settings = application_settings
        self.service_name = service_name

        self.__bp_trace = BlackPearlTrace(
            trace_id=BlackPearlTrace._generateTraceId(),
            span_service_name=self.service_name,
            span_service_host='localhost:'+str(self.port),
        )

        self._post_init()

    def before_run(self, *args,**kwargs):
        pass

    def _post_init(self):
        BlackPearlUOM.__bp_trace = self.__bp_trace

        logger.info('post initialization ...')
        for i in self.modules:
            BlackPearlUOM.importModule(i)
        module_handers = BlackPearlUOM.load((BlackPearlRequestHandler,))
        self.handlers += module_handers
        self.application_settings['debug'] = self.debug

        logger.info(BlackPearlUOM.info())

    def run(self, *args, **kwargs):
        logger.info("before running server, do ...")
        self.before_run(*args, **kwargs)

        logger.info("running server http://localhost:"+str(self.port))

        if self.debug:
            logger.info('handler count: '+str(len(self.handlers)))
            logger.info('modules count: '+str(len(self.modules)))
            logger.info('app settings:  '+str(self.application_settings))

        # run.
        application = tornado.web.Application( self.handlers, **self.application_settings )
        application.service_name = self.service_name
        application.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()
