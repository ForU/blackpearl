#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ht <515563130@qq.com, weixin:jacoolee>

import time
import random

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
