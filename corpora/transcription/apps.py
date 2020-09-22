# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class TranscriptionConfig(AppConfig):
    name = 'transcription'

    def ready(self):
        import transcription.signals
