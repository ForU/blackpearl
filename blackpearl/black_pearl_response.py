#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Thu Jun 25 11:02:25 2015
# ht <515563130@qq.com, weixin:jacoolee>

# normal response and error response

import json
import random

from black_pearl_constants import Constants

class Response(object):
    def __init__(self, result=None, code=Constants.RC_SUCCESS, why='', extra={}, use_raw_data=False, request_id=''):
        self.code = code
        self.why = why
        self.result = result
        self.extra = extra
        self.use_raw_data = use_raw_data
        self.request_id = request_id

    def convert(self):
        if self.use_raw_data:
            return self.result

        d = {
            'code': self.code.code,
            'info': self.code.info,
            'why': self.why,
            'result': self.result,
            'extra': self.extra,
        }
        return json.dumps( d )
