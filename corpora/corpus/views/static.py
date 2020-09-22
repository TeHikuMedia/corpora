# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views import View
from django.http import HttpResponse

import logging
logger = logging.getLogger('corpora')


class WaveWorker(View):
    '''
    Basically serves a static file because of how we made stuff we need a hack for now.
    '''

    def get(self, request, *args, **kwargs):
        file = open('corpus/templates/corpus/js/waveWorker.min.js', 'r')
        response = HttpResponse(content=file)
        response['Content-Type'] = "text/javascript;charset=UTF-8"
        return response

class EncoderWorker(View):
    '''
    Basically serves a static file because of how we made stuff we need a hack for now.
    '''

    def get(self, request, *args, **kwargs):
        file = open('corpus/templates/corpus/js/encoderWorker.min.js', 'r')
        response = HttpResponse(content=file)
        response['Content-Type'] = "text/javascript;charset=UTF-8"
        return response

class EncoderWorkerWasm(View):
    '''
    Basically serves a static file because of how we made stuff we need a hack for now.
    '''

    def get(self, request, *args, **kwargs):
        file = open('corpus/templates/corpus/js/encoderWorker.min.wasm', 'rb')
        response = HttpResponse(content=file)
        response['Content-Type'] = "application/wasm"
        return response
