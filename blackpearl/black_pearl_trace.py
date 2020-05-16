#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ht <weixin:jacoolee>

import time
import random
import json

class BlackPearlTrace(object):
    def __init__(self,
                 trace_id='',
                 timestamp=0,
                 duration=0,
                 span_service_name='',
                 span_service_host='',
                 span_ordered_id=0 ):
        # trace metas
        self.trace_id = trace_id
        self.timestamp = timestamp
        self.duration = duration
        self.span_service_name = span_service_name
        self.span_service_host = span_service_host
        self.span_ordered_id = span_ordered_id

    def __str__(self):
        return '-'.join([
            self.trace_id,
            self.span_service_name+':'+self.span_service_host+':'+str(self.span_ordered_id)
        ])

    def __repr__(self):
        return json.dumps({
            'trace_id': self.trace_id,
            'duration': str(self.duration),
            'span_service_name': self.span_service_name,
            'span_service_host': self.span_service_host,
            'span_ordered_id': str(self.span_ordered_id)
        })

    @classmethod
    def _generateTraceId(cls):
        return ''.join([
            hex(int(float(time.time())*1000))[2:],
            hex(int(float(str(random.random())[2:])))[2:6],
            hex(int(float(str(random.random())[2:])))[2:6],
        ]).upper()

class BlackPearlWebHandlerTrace(BlackPearlTrace):
    def __init__(self, handler):
        self.__handler = handler

        # trace metas
        super(BlackPearlWebHandlerTrace, self).__init__(
            trace_id = self._getTraceId(),
            span_service_name = self._getServiceName(),
            span_service_host = self._getServiceHost(),
            span_ordered_id = self._getSpanOrderedId(),
        )

    def _getTraceId(self):
        trace_id = self.__handler.request.headers.get('trace_id', None)
        if trace_id:
            return trace_id
        return self._generateTraceId()

    def _getServiceName(self):
        return self.__handler.application.service_name

    def _getServiceHost(self):
        return self.__handler.request.host

    def _getSpanOrderedId(self):
        return int(self.__handler.request.headers.get('span_ordered_id', 0))
