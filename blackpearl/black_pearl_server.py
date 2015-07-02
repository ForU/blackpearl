#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Mon May  4 16:59:45 2015
# ht <515563130@qq.com, weixin:jacoolee>

import tornado.ioloop
import tornado.web

from black_pearl_uom import BlackPearlUOM
from black_pearl_request import BlackPearlRequestHandler

class BlackPearlServer(object):
    def __init__(self, configure_manager=None):
        self.cm = configure_manager
        self.handlers = None

    def init(self):
        print "initializing server ..."
        BlackPearlUOM.importModule('api')
        # ...
        self.handlers = BlackPearlUOM.load((BlackPearlRequestHandler,))
        print BlackPearlUOM.info()

    def run(self):
        print "running server @localhost:8888 ..."
        # TODO Mon May  4 17:00:35 2015 [load from configure file]
        application = tornado.web.Application( self.handlers )
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    svr = BlackPearlServer()
    svr.init()
    svr.run()
