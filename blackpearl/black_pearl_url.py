#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
http uri:rfc3986 parser

wiki: http://en.wikipedia.org/wiki/URI_scheme
"""

from black_pearl_exception import NotImplementedInterface


PARAMS_SEPARATOR_AMPERSAND = '&'
PARAMS_SEPARATOR_SEMICOLON = ';'


class BlackPearlBaseUrl(object):
    def __init__(self, raw_url):
        self._raw_url = raw_url
        self._url = raw_url
        self._valid = False

    def refine(self):
        self._parse(self._url, refine_url=True)
        return self._url

    def _parse(self, *kargs, **kwargs):
        raise NotImplementedInterface()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self._url

class BlackPearlUrl(BlackPearlBaseUrl):
    """sample: /A/B/C/D/.../X?k1=v1&k2=v2&...&kN=vN
    """
    def __init__(self, raw_url):
        super(BlackPearlUrl, self).__init__(raw_url)
        self._path = []
        self._params = {}

    def _parse(self, url, kv_separator=PARAMS_SEPARATOR_AMPERSAND, refine_url=False, ):
        """parse @url to get #path and #params
        """
        # IM: bug-protential when treat '?' as first split seperator
        l_qmark = url.split('?', 1)
        path   = l_qmark[0] or None
        params = l_qmark[1] if 2 == len(l_qmark) else None

        if path:
            self._valid = True
            if path.startswith('/'):
                path = path[1:]
            self._path = [i.strip() for i in path.split('/') if i.strip()]

        if params:
            l_kv_pairs = params.split(kv_separator)
            for kv_pair in l_kv_pairs:
                kv_pair = kv_pair.strip()
                if not kv_pair:
                    continue
                l = kv_pair.split('=', 1)
                k = l[0].strip() or None
                if not k:
                    continue
                v = l[1].strip() if k and 2 == len(l) else None
                self._params[k] = v or None

        if refine_url:
            self._url = '/'
            self._url += '/'.join(self._path)
            self._url += '?'
            self._url += '&'.join(['%s=%s'%(k,v or '') for k,v in self._params.items()])
