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
import urllib2

from black_pearl_uom import BlackPearlUOM
from black_pearl_constants import Constants
from black_pearl_response import Response
from black_pearl_error import ResponseException
from black_pearl_utils import Magic
from black_pearl_exception import Break
from black_pearl_trace import BlackPearlWebHandlerTrace

def dia(enable=True):
    def dec(f):
        @functools.wraps(f)
        def _f_wrapper(*args, **kwargs):
            if enable:
                # time
                s = time.time() * 1000
                f_ret_val = f(*args, **kwargs)
                e = time.time() * 1000

                # get uri by self.xxx
                req_handler = args[0]
                req_handler._bp_trace.timestamp = s
                req_handler._bp_trace.duration = e-s

                req_handler._on_request_diagnose(*args, **kwargs)

                return f_ret_val
            return f(*args, **kwargs)
        return _f_wrapper
    return dec


debug = False

class BlackPearlRequestHandler(tornado.web.RequestHandler):
    def _get_interface(self):
        # CRITICAL: simple
        if '?' in self.request.uri:
            url_pattern = self.request.uri.split('?')[0].strip()
        else:
            url_pattern = self.request.uri
        return ( url_pattern, url_pattern.split('/')[-1].strip() )

    def _get_iface_params(self, iface_complete, generic_args_restriction={}):
        iface_args = BlackPearlUOM.getArgs(iface_complete)

        # process iface defined arguments
        if not iface_args:
            raise ResponseException(Constants.RC_NEVER_HAPPEN, why="unregistered '%s'" % iface_complete)
        iface_params, iface_restriction = iface_args[0], iface_args[1]

        self._inject_refine_iface_args(iface_complete, iface_params, iface_restriction)

        # CRITICAL: has parameter but no restriction
        if iface_params and not iface_restriction:
            raise ResponseException( Constants.RC_IFACE_UNPROPERLY_DEFINED,
                                     why='refer to iface definition guide plz~' )


        # process generic defined arguments
        if not isinstance( generic_args_restriction, dict):
            raise ResponseException( Constants.RC_IFACE_UNPROPERLY_DEFINED,
                                     why='generic arguments restrict should be a dict' )

        generic_args_restriction = { k: Magic( required    = v.get('required'),
                                               type        = v.get('type'),
                                               default     = v.get('default'),
                                               value_enum  = v.get('value_enum'),
                                               value_range = v.get('value_enum')
                                           )
                                        for k,v in generic_args_restriction.items()}

        generic_parameters = self._get_iface_params_from_request_by_restrict(iface_complete, self.request.body_arguments, generic_args_restriction)
        iface_parameters = self._get_iface_params_from_request_by_restrict(iface_complete, self.request.body_arguments, iface_restriction)
        return iface_parameters, generic_parameters


    def _get_iface_params_from_request_by_restrict(self, iface_complete, request_arguments, arguments_restriction):
        parameters , req_args = {}, request_arguments
        for k,v in arguments_restriction.items():
            if not isinstance(v, Magic):
                raise ResponseException( Constants.RC_IFACE_UNPROPERLY_DEFINED, why='refer to iface definition guide plz~' )

            val = req_args.get(k,[None])[0]

            if v.required and val == None:

                why = "[FATAL] '%s' is required for iface:'%s'" % (k, iface_complete)
                raise ResponseException(Constants.RC_IFACE_INVALID_PARAMETER, why=why)
            param_v = urllib2.unquote(str(val)) if val != None else v.default

            # auto convert.
            if v.type:
                try:
                    # CRITICAL: we allow None show as it is to API other than typed.
                    if param_v is not None:
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

    def _before_get(self, generic_parameters, parameters):
        """@return Ok, Response
        default: True, Response(code=Constants.RC_SUCCESS)
        """
        return True, Response(code=Constants.RC_SUCCESS)

    def _after_get(self, generic_parameters, parameters):
        """@return Ok, Response
        default: True, Response(code=Constants.RC_SUCCESS)
        """
        return True, Response(code=Constants.RC_SUCCESS)

    def _very_before_get(self, *args, **kwargs):
        """
        return: a dict as: { genericArgName: genericArgRestrict }
        """
        return True, None

    def _very_after_get(self, response):
        return response.convert()

    def _inject_refine_iface_args(self, iface_complete, iface_params, iface_restriction):
        pass

    def _inject_generic_arguments(self):
        """
        return: a dict as: { genericArgName: genericArgRestrict }
        """
        return {}

    def _on_request_start(self, *args, **kwargs):
        pass

    def _on_request_diagnose(self, *args, **kwargs):
        pass

    def _on_process_exception_Break(self, e):
        pass

    def _on_process_exception_ResponseException(self, e):
        pass

    def _on_process_exception_Exception(self, e):
        pass

    def _on_write_exception_Exception(self, e):
        pass


    @dia(enable=True)
    def get(self, *args, **kwargs):
        """ do all magic here"""
        response = None
        resp = Response(code=Constants.RC_SUCCESS)
        ok = True

        try:
            # based on nginx configure
            self._bp_ip = self.request.headers.get('X-Forwarded-For', '')
            self._bp_trace = BlackPearlWebHandlerTrace(handler=self)

            self._on_request_start(*args, **kwargs)


            # very before get
            ok, resp = self._very_before_get(self, *args, **kwargs)
            if not ok:      # overwrite the real response only not ok
                response = resp
                raise Break('_very_before_get, coz:' + str(response.code))

            iface_complete, iface = self._get_interface()
            parameters, generic_parameters = self._get_iface_params(iface_complete, self._inject_generic_arguments()) or {}

            # CRITICAL: before get
            # _before_get_xxxxx has high priority than the shared function:_before_get.
            # if has no such function:_before_get_xxxxx, use the default shared one
            # f = getattr(self, '_before_get_'+iface, None)
            # if f is not None:
            #     ok, resp = f(**parameters)
            # else:

            ok, resp = self._before_get(generic_parameters, parameters)
            if not ok:      # overwrite the real response only not ok
                response = resp
                raise Break('_before_get, coz:' + str(response.code))

            # getattr(self, '_after_get_'+iface)(**parameters) # TODO: fine-gained controller
            # real get
            response = getattr(self, iface)(**parameters)
            try:
                ok, resp = getattr(self, '_after_get_'+iface)(generic_parameters, parameters)
            except AttributeError as e:
                ok, resp = self._after_get(generic_parameters, parameters)
            finally:
                if not ok:      # overwrite the real response only not ok
                    response = resp
                    raise Break('_after_get, coz:' + str(response.code))

        except Break as e:
            # CRITICAL: here we do not modify the response.
            self._on_process_exception_Break(e)
        except ResponseException as e:
            self._on_process_exception_ResponseException(e)
            response = Response(code=e.response_code, why=str(e.why) if debug else '')
        except Exception as e:
            self._on_process_exception_Exception(e)
            response = Response(code=Constants.RC_UNKNOWN, why=('Normal Process Exception:'+str(e)) if debug else '')

        try:
            # FIXME
            self.add_header('Access-Control-Allow-Origin', '*')
            self.add_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')

            resp = self._very_after_get(response)
            self.write( resp )
            return
        except Exception as e:
            self._on_write_exception_Exception(e)
            response = Response(code=Constants.RC_JSON_DUMPS_FAILED, why=str(e))

            resp = self._very_after_get(response)
            self.write( resp )

    # https://stackoverflow.com/questions/44900282/warningtornado-access405-error-stopping-post-from-both-localhost-and-file
    post = options = get

#    def post(self, *args, **kwargs):
#        self.get(*args, **kwargs)

#    def options(self, *args, **kwargs):
#        self.get(*args, **kwargs)



