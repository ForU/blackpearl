#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Mon May  4 13:44:29 2015
# ht <515563130@qq.com, weixin:jacoolee>

"""
black pearl error-related stuff
"""

class ResponseException(Exception):
    def __init__(self, response_code, why=None, *args, **kwargs):
        self.response_code = response_code
        self.why = why
        super(ResponseException, self).__init__(*args, **kwargs)
        print 'ResponseException: response_code:%s, %s, %s' % (response_code, args, kwargs)
