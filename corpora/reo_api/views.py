# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.shortcuts import render

from django.views.generic.base import TemplateView
from corpora.mixins import SiteInfoMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from people.views.stats_views import JSONResponseMixin
from django.views import View

from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.documentation import get_docs_view
from rest_framework.renderers import (
    CoreJSONRenderer, DocumentationRenderer, SchemaJSRenderer
)
from rest_framework.schemas import SchemaGenerator, get_schema_view
from rest_framework import authentication, permissions
from rest_framework.schemas import AutoSchema
from rest_framework.response import Response

from people.helpers import get_person
from rest_framework.authtoken.models import Token

from django.templatetags.static import static

import logging
logger = logging.getLogger('corpora')


class HomeView(SiteInfoMixin, TemplateView):
    template_name = "reo_api/home.html"
    x_title = _('kōreromāori.io')
    x_description = _('Indigenous language tools powered by machine learning.')
    x_image = static("reo_api/img/icon.png")


class DocsDashboardView(SiteInfoMixin, TemplateView):
    template_name = "reo_api/docs.html"
    x_title = _('Documentation')
    x_description = _('API documentation.')
    x_image = static("reo_api/img/icon.png")


class BrowseAPIDashboardView(SiteInfoMixin, TemplateView):
    template_name = "reo_api/api_browse.html"
    x_title = _('Browseable API')
    x_description = _('Browseable API.')
    x_image = static("reo_api/img/icon.png")


class TokenView(
        JSONResponseMixin, UserPassesTestMixin, View):

    def render_to_response(self, context):
        return self.render_to_json_response(context)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context(request))

    def post(self, request, *args, **kwargs):
        person = get_person(request)
        token, created = Token.objects.get_or_create(user=person.user)
        return self.render_to_response({'token': token.key})

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context(self, request):
        person = get_person(request)
        token = Token.objects.get(user=person.user)
        return {'token': token.key}
