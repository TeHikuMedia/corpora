# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from django.utils.translation import ugettext_lazy as _

from rest_framework.documentation import include_docs_urls

from django.urls.resolvers import RegexURLPattern

from transcription.views.api import AudioFileTranscriptionViewSet
from rest_framework import routers

router = routers.DefaultRouter()


