#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
black pearl exceptions
"""

class BlackPearlException(Exception):
    def __init__(self, *args, **kwargs):
        super(BlackPearlException, self).__init__(*args, **kwargs)

class Break(BlackPearlException):
    def __init__(self, *args, **kwargs):
        super(Break, self).__init__(*args, **kwargs)

class NotImplementedInterface(BlackPearlException):
    pass


