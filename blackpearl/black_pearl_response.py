#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Thu Jun 25 11:02:25 2015
# ht <515563130@qq.com, weixin:jacoolee>

# normal response and error response

import json

from black_pearl_constants import Constants


class Response(object):
    def __init__(self, result=None, code=Constants.RC_SUCCESS, why='', extra={}):
        self.code = code
        self.why = why
        self.result = result
        self.extra = extra

    def dumpAsJson(self):
        d = { 'code': self.code.code,
              'info': self.code.info,
              'why': self.why,
              'result': self.result,
              'extra': self.extra
          }
        try:
            return json.dumps( d )
        except Exception as e:
            print "failed to dump response as json, raise exception"
            raise e
