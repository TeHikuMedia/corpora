# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class MessageConfig(AppConfig):
    name = 'message'

    def ready(self):
        import message.signals
