#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
black pearl exceptions
"""

class BlackPearlException(Exception):
    def __init__(self, ):
        self.what = self.message

    @property
    def what(self):
        return self.message


class NotImplementedInterface(BlackPearlException):
    pass


