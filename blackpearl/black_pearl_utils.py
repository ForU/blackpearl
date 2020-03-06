#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ht <515563130@qq.com, weixin:jacoolee>

from datetime import datetime

class BareBone(object):
    def __init__(self, *args, **kwargs):
        pass


class Magic(object):
    def __init__(self, *args, **kwargs):
        self.__raw__ = kwargs
        setattr(self, 'args', args)
        for k,v in kwargs.items():
            setattr(self, k, v)

    def __str__(self,):
        return str(self.__dict__)


class DeepMagic(object):
    def __init__(self, *args, **kwargs):
        self.__raw__ = kwargs
        setattr(self, 'args', args)
        def __inner_do_magic(obj, d):
            for k,v in d.items():
                if not isinstance(v, dict):
                    setattr(obj, k, v)
                    continue
                else:
                    setattr(obj, k, BareBone())
                    bbone = getattr(obj, k)
                    __inner_do_magic( bbone, v )

        # main
        __inner_do_magic(self, kwargs)



class log(object):
    WHITE     = '\033[0m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    ORANGE    = '\033[33m'
    BLUE      = '\033[34m'
    PURPLE    = '\033[35m'

    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

    BRED      = '\033[41m'
    BGREEN    = '\033[42m'
    BYELLOW   = '\033[43m'
    BBLUE     = '\033[44m'
    BPINK     = '\033[45m'
    BCYAN     = '\033[46m'

    ENDC      = '\033[0m'


    @classmethod
    def _strip_request_id(cls, kwargs):
        _request_id = kwargs.get('_request_id', None)
        if _request_id is not None:
            del kwargs['_request_id']
        else:
            _request_id = ''
        return _request_id

    @classmethod
    def error(cls, *args, **kwargs):
        _rqid = cls._strip_request_id(kwargs)
        print _rqid, '[' + datetime.now().strftime('%y-%m-%d %H:%M:%S.%f') + '] ' + cls.RED + cls.BOLD + "BLACKPEARL ERROR: " + " ".join([str(i) for i in args]) + " ".join([k+'='+kwargs[k] for k in kwargs.keys()]) + cls.ENDC

    @classmethod
    def warn(cls, *args, **kwargs):
        _rqid = cls._strip_request_id(kwargs)
        print _rqid, '[' + datetime.now().strftime('%y-%m-%d %H:%M:%S.%f') + '] ' + cls.WARNING + cls.BOLD + "BLACKPEARL WARN: " + " ".join([str(i) for i in args]) + " ".join([k+'='+kwargs[k] for k in kwargs.keys()]) + cls.ENDC

    @classmethod
    def debug(cls, *args, **kwargs):
        _rqid = cls._strip_request_id(kwargs)
        print _rqid, '[' + datetime.now().strftime('%y-%m-%d %H:%M:%S.%f') + '] ' + cls.OKBLUE + "BLACKPEARL DEBUG: " + " ".join([str(i) for i in args]) + " ".join([k+'='+kwargs[k] for k in kwargs.keys()]) + cls.ENDC

    @classmethod
    def hidebug(cls, *args, **kwargs):
        _rqid = cls._strip_request_id(kwargs)
        print _rqid, '[' + datetime.now().strftime('%y-%m-%d %H:%M:%S.%f') + '] ' + cls.BOLD+ cls.WHITE + cls.BCYAN + "BLACKPEARL DEBUG: " + " ".join([str(i) for i in args]) + " ".join([k+'='+kwargs[k] for k in kwargs.keys()]) + cls.ENDC

    @classmethod
    def dia(cls, *args, **kwargs):
        _rqid = cls._strip_request_id(kwargs)
        print _rqid, '[' + datetime.now().strftime('%y-%m-%d %H:%M:%S.%f') + '] ' + cls.PURPLE + "BLACKPEARL DIA: " + " ".join([str(i) for i in args]) + " ".join([k+'='+kwargs[k] for k in kwargs.keys()]) + cls.ENDC

    @classmethod
    def info(cls, *args, **kwargs):
        _rqid = cls._strip_request_id(kwargs)
        print _rqid, '[' + datetime.now().strftime('%y-%m-%d %H:%M:%S.%f') + '] ' + "BLACKPEARL INFO: " + " ".join([str(i) for i in args]) + " ".join([k+'='+kwargs[k] for k in kwargs.keys()]) + cls.ENDC
