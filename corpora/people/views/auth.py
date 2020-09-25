# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from corpora.mixins import EnsureCsrfCookieMixin
from rest_framework.authtoken.models import Token
from django.views.generic.base import TemplateView
from django.core.cache import cache

import logging
logger = logging.getLogger('corpora')
# sudo cat /webapp/logs/django.log


class ProcessExpoRedirect(
        EnsureCsrfCookieMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        redirect_url = cache.get(
            'EXPO-REDIRECT-URL',
            'https://auth.expo.io/@kmahelona/corpora-expo')
        if request.user.is_authenticated:
            token, created = Token.objects.get_or_create(user=request.user)
            cache.delete('EXPO-REDIRECT-URL')

            login_uuid = request.get_signed_cookie('uuid-expo-login', None)
            cache.delete(
                'USER-LOGIN-FROM-EXPO-{0}'.format(
                    login_uuid))

            location = "{0}?token={1}".format(redirect_url, token.key)
            res = HttpResponse(location, status=302)
            res['Location'] = location
            return res

            return HttpResponseRedirect(
                "{0}?token={1}".format(redirect_url, token.key)
            )

        else:
            return HttpResponseRedirect('/')
