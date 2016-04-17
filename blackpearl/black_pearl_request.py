#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A more features added request wrapper
"""
import traceback

import tornado
import time
import functools
import json

from black_pearl_uom import BlackPearlUOM
from black_pearl_constants import Constants
from black_pearl_response import Response
from black_pearl_error import ResponseException
from black_pearl_utils import Magic
from black_pearl_exception import Break


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
                print '- response: ' + req_handler.request.uri + " => " + str(f_ret_val) if f_ret_val else ''
                return f_ret_val
            return f(*args, **kwargs)
        return _f_wrapper
    return dec


debug = False 

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
                raise ResponseException( Constants.RC_IFACE_UNPROPERLY_DEFINED, why='refer to iface definition guide plz~' )

            val = req_args.get(k,[None])[0]
            if v.required and val == None:
                why = "[FATAL] '%s' is required for iface:'%s'" % (k, iface_complete)
                raise ResponseException(Constants.RC_IFACE_INVALID_PARAMETER, why=why)
            param_v = val if val != None else v.default

            # auto convert.
            if v.type:
                try:
                    param_v = v.type(param_v)
                except Exception as e:
                    why = "[FATAL] '%s' of '%s' need to be '%s' compatible, '%s'" % (v,k,str(v.type),e)
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

    def _before_get(self, *args, **kwargs):
        """@return Ok, Response
        default: True, Response(code=Constants.RC_SUCCESS)
        """
        return True, Response(code=Constants.RC_SUCCESS)

    def _after_get(self, *args, **kwargs):
        """@return Ok, Response
        default: True, Response(code=Constants.RC_SUCCESS)
        """
        return True, Response(code=Constants.RC_SUCCESS)

    @dia(enable=True)
    def get(self, *args, **kwargs):
        print str(self.cookies)
        """ do all magic here"""
        print 'TODO session_id:', self.get_cookie('session_id')
        try:
            iface_complete, iface = self._get_interface()
            parameters = self._get_iface_params(iface_complete) or {}

            response = None
            resp = Response(code=Constants.RC_SUCCESS)
            ok = True

            # CRITICAL: before get
            # _before_get_xxxxx has high priority than the shared function:_before_get.
            # if has no such function:_before_get_xxxxx, use the default sharedone
            try:
                ok, resp = getattr(self, '_before_get_'+iface)(**parameters)
            except AttributeError as e:
                ok, resp = self._before_get(*args, **kwargs)
            finally:
                if not ok:      # overwrite the real response only not ok
                    response = resp
                    raise Break('_before_get')

            # getattr(self, '_after_get_'+iface)(**parameters) # TODO: fine-gained controller

            # real get
            response = getattr(self, iface)(**parameters)
            to_break = True

            try:
                ok, resp = getattr(self, '_after_get_'+iface)(**parameters)
            except AttributeError as e:
                ok, resp = self._after_get(*args, **kwargs)
            finally:
                if not ok:      # overwrite the real response only not ok
                    response = resp
                    raise Break('_after_get')

        except Break as e:
            # CRITICAL: here we do not modify the response.
            print "Break for "+str(e)
        except ResponseException as e:
            print "Normal Process ResponseException: %s" % (e)
            # TODO only debug mode show the why to api caller
            response = Response(code=e.response_code, why=str(e.why) if debug else '')
        except Exception as e:
            traceback.print_exc()
            print "Normal Process Exception: %s" % (e)
            response = Response(code=Constants.RC_UNKNOWN, why=('Normal Process Exception:'+str(e)) if debug else '')

        try:
            # FIXME
            self.add_header('Access-Control-Allow-Origin', '*')
            self.write( response.dumpAsJson() )
            return
        except Exception as e:
            # if write fails, the requester never get data, so the
            # only soundable and valuable reason for client is that
            # F:json.dumps fails.
            # print "WRITE Exception caught: %s" % (e)
            response = Response(code=Constants.RC_JSON_DUMPS_FAILED, why=str(e))
            self.write( response.dumpAsJson() )

    @dia(enable=True)
    def post(self, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
        self.get(*args, **kwargs)


