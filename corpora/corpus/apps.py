from __future__ import unicode_literals

from django.apps import AppConfig


class CorpusConfig(AppConfig):
    name = 'corpus'

    def ready(self):
        import corpus.signals
