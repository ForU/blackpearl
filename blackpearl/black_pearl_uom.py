#! /usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import types

from black_pearl_utils import Magic, log


import tornado
class DocRequestHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write(BlackPearlUOM.info())


class BlackPearlUOM(object):
    module_objs = []
    # key: url_pattern
    # value: (parameter_names=[...], defaults={...})
    interface_infos = {}

    @classmethod
    def importModule(cls, module):
        if isinstance(module, str):
            try:
                module = __import__(module)
            except Exception as e:
                log.error("[ERROR] failed to import '%s', caz:'%s'" % (module, e))
                return
        cls.module_objs.append(module)

    @classmethod
    def info(cls):
        interfaces = ''
        for k,v in cls.interface_infos.items():
            interfaces +=( "%s %s\n" % (k, v))

        return str(cls.module_objs) + '\n' + '_'*100 + '\n' + interfaces

    @classmethod
    def _get_classes_from_module(cls, module_obj, BaseClassTypes=(object,)):
        """expose classes who are class-type and
           sub-class of specified base class types.
        """
        return [v for _,v in module_obj.__dict__.items() if inspect.isclass(v) and issubclass(v, BaseClassTypes) and v not in BaseClassTypes]

    @classmethod
    def _get_functions_from_class(cls, class_obj, only_public=True):
        return [v for _,v in class_obj.__dict__.items() if type(v) == types.FunctionType and (not v.__name__.startswith('_') if only_public else True)]

    @classmethod
    def _get_args_from_function(cls, function_obj):
        """more restriction on interface comes here.
        'required', 'type', 'default', 'enum', 'range', ...
        """
        fargspec = inspect.getargspec(function_obj)
        f_args, f_defaults = fargspec.args, fargspec.defaults
        log.debug("_get_args_from_function:", function_obj.__name__, "f_args:", f_args, "f_defaults:", f_defaults)
        default_args = {}
        if f_defaults:
            default_args = { i[0]:i[1] for i in zip(f_args[::-1], f_defaults[::-1]) }
            default_args = { p: # value
                             Magic( required    = v.get('required'),
                                    type        = v.get('type'),
                                    default     = v.get('default'),
                                    value_enum  = v.get('value_enum'),
                                    value_range = v.get('value_enum')
                                )
                             for p,v in default_args.items() }
        # remove 'cls'/'self' if exists
        if f_args and f_args[0] in ('cls', 'self'):
            f_args = f_args[1:]
        return (f_args, default_args)

    @classmethod
    def _gen_url_pattern(cls, module_name, class_name, iface_name):
        return "/%s/%s/%s" % (module_name, class_name, iface_name)

    @classmethod
    def load(cls, BaseClassTypes=(object,)):
        handlers = []
        for mod in cls.module_objs:
            for c in cls._get_classes_from_module(mod, BaseClassTypes):
                for f in cls._get_functions_from_class(c):
                    url_pattern = cls._gen_url_pattern(mod.__name__, c.__name__, f.__name__)
                    cls.interface_infos[url_pattern] = cls._get_args_from_function(f)
                    log.info("registering handler:", (url_pattern, c))
                    handlers.append( (url_pattern, c) )
        # register doc
        handlers.append(('/docs', DocRequestHandler))
        return handlers

    @classmethod
    def getArgs(cls, url_pattern):
        return cls.interface_infos.get(url_pattern)
