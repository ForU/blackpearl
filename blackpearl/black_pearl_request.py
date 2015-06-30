#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A more features added request wrapper
"""

import tornado
import time
import functools
import json

from black_pearl_uom import BlackPearlUOM
from black_pearl_constants import Constants
from black_pearl_response import Response
from black_pearl_error import ResponseException
from black_pearl_utils import Magic


def dia(enable=True):
    def dec(f):
        @functools.wraps(f)
        def _f_wrapper(*args, **kwargs):
            if enable:
                # time
                s = time.time()
                f_ret_val = f(*args, **kwargs)
                e = time.time()

                # get uri by self.xxx
                req_handler = args[0]
                # TODO Fri Apr  3 02:48:39 2015
                # more ...
                print "- [%s] %s timecost:%6fms, remote_ip:'%s', api:'%s' -" % (time.asctime(), req_handler.request.method, (e-s)*1000, req_handler.request.remote_ip, req_handler.request.uri)

                return f_ret_val
            return f(*args, **kwargs)
        return _f_wrapper
    return dec


class BlackPearlRequestHandler(tornado.web.RequestHandler):
    def _show_request(self, whole=False):
        keys = self.request.__dict__.keys()
        keys.sort()
        print '_'*100
        for k in keys:
            if whole:
                v = str(self.request.__dict__[k])
            else:
                v = str(self.request.__dict__[k])[:80]
            print "| %15s | %s" % (k, v)
        print '_'*100

    def _get_interface(self):
        # CRITICAL: simple
        if '?' in self.request.uri:
            url_pattern = self.request.uri.split('?')[0].strip()
        else:
            url_pattern = self.request.uri
        return ( url_pattern, url_pattern.split('/')[-1].strip() )

    def _get_iface_params(self, iface_complete):
        iface_args = BlackPearlUOM.getArgs(iface_complete)
        if not iface_args:
            raise ResponseException(Constants.RC_NEVER_HAPPEN, why="unregistered '%s'" % iface_complete)
        iface_params, iface_restriction = iface_args[0], iface_args[1]

        # CRITICAL: has parameter but no restriction
        if iface_params and not iface_restriction:
            raise ResponseException( Constants.RC_IFACE_UNPROPERLY_DEFINED,
                                     why='refer to iface definition guide plz~' )

        parameters , req_args = {}, self.request.arguments
        for k,v in iface_restriction.items():
            if not isinstance(v, Magic):
                raise ResponseException( Constants.RC_IFACE_UNPROPERLY_DEFINED,
                                         why='refer to iface definition guide plz~' )
            if v.required:
                if k not in req_args:
                    why = "[FATAL] '%s' is required of iface:'%s'" % (k, iface_complete)
                    raise ResponseException(Constants.RC_IFACE_INVALID_PARAMETER, why=why)
                else:
                    param_v = req_args.get(k,[None])[0]
            else:
                param_v = v.default
            try:
                param_v = v.type(param_v)
            except Exception as e:
                why = "[FATAL] '%s' of '%s' need to be '%s' compatible, '%s'" % (v,k,v.type,e)
                raise ResponseException(Constants.RC_IFACE_INVALID_PARAMETER, why=why)

            # check param_v no matter where do we get it!
            if v.value_enum and param_v not in v.value_enum:
                why = "[FATAL] '%s' of key:'%s' not in enum:'%s'" % (param_v, k, v.value_enum)
                raise ResponseException(Constants.RC_IFACE_INVALID_PARAMETER, why=why)
            elif v.value_range and not (v.value_range[0] <= param_v <= v.value_range[1]):
                why = "[FATAL] '%s' of key:'%s' not in range:'%s'" % (param_v, k, v.value_enum)
                raise ResponseException(Constants.RC_IFACE_INVALID_PARAMETER, why=why)
            else:
                parameters[k] = param_v
            return parameters

    @dia(enable=True)
    def get(self, *args, **kwargs):
        """ do all magic here"""
        print 'session_id:', self.get_cookie('session_id')
        try:
            iface_complete, iface = self._get_interface()
            parameters = self._get_iface_params(iface_complete) or {}
            response = getattr(self, iface)(**parameters)
        except ResponseException as e:
            print e
            response = Response(code=Constants.RC_UNKNOWN, why=str(e))
        except Exception as e:
            print e
            response = Response(code=Constants.RC_UNKNOWN, why=str(e))
        try:
            self.write( response.dumpAsJson() )
            return
        except Exception as e:
            # if write fails, the requester never get data, so the
            # only soundable and valuable reason for client is that
            # F:json.dumps fails.
            print e
            response = Response(code=Constants.RC_JSON_DUMPS_FAILED, why=str(e))
            self.write( response.dumpAsJson() )

    def post(self, *args, **kwargs):
        import ipdb; ipdb.set_trace()

        self.get(*args, **kwargs)
