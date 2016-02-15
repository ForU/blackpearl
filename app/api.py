#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web

from blackpearl.black_pearl_request import BlackPearlRequestHandler
from blackpearl.black_pearl_response import Response

from app_error import AppConstants


class common(BlackPearlRequestHandler):
    def test(self,id={'type':str,'required':True},id2={'type':int,'required':True}):
       return Response(AppConstants.RC_SUCCESS, result={'ok':True})
