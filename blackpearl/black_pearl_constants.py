#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Mon May  4 13:43:41 2015
# ht <515563130@qq.com, weixin:jacoolee>


class ResponseCode(object):
    def __init__(self, code, info=None, *args, **kwargs):
        """id is a int number
        info can be anything used for describe current response id.
        """
        self.code = code
        self.info = info

    def __str__(self):
        return "code:%s, info:%s" % (self.code, self.info)

class Constants(object):
    """
    CRITICAL ERROR CONVENTION:

    code < 0: black pearl internal error
    code = 0: OK
    code > 0: APP-specific error

    And, inherient Constants to add your own response codes.
    """
    RC_JSON_DUMPS_FAILED = ResponseCode(-5, '生成json失败')
    RC_IFACE_INVALID_PARAMETER = ResponseCode(-4, '参数错误')
    RC_NEVER_HAPPEN = ResponseCode(-3, '应该不会发生')
    RC_IFACE_UNPROPERLY_DEFINED = ResponseCode(-2, '接口定义格式非法')
    RC_UNKNOWN = ResponseCode(-1, '未知错误')
    RC_SUCCESS = ResponseCode(0, 'OK')
