#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Thu Jun 25 11:02:25 2015
# ht <515563130@qq.com, weixin:jacoolee>

# normal response and error response

import json
import random

from black_pearl_constants import Constants
from black_pearl_utils import log

class Response(object):
    def __init__(self, result=None, code=Constants.RC_SUCCESS, why='', extra={}, use_raw_data=False):
        self.code = code
        self.why = why
        self.result = result
        self.extra = extra
        self.use_raw_data = use_raw_data

    def convert(self):
        if self.why:
            log.error('Response: code =', self.code, ', why =', self.why)
        else:
            log.dia('Response: code =', self.code, ', no why')

        if self.use_raw_data:
            return self.result

        d = {
            'code': self.code.code,
            'info': self.code.info,
            'why': self.why,
            'result': self.result,
            'extra': self.extra,
        }
        try:
            return json.dumps( d )
        except Exception as e:
            log.error( "Response: failed to dump response as json, raise exception")
            raise e
