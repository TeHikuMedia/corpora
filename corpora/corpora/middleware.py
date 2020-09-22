# -*- coding: utf-8 -*-

from django.utils import translation
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from people.helpers import get_current_language, get_or_create_person
from people.models import KnownLanguage
from license.models import SiteLicense, License
from django.contrib.sites.shortcuts import get_current_site

from corpus.base_settings import LANGUAGE_DOMAINS

from urllib.parse import parse_qs

from uuid import uuid4 as uuid

import logging
logger = logging.getLogger('corpora')


class PersonMiddleware(object):
    '''
    This middleware sets a uuid cookie so we can collect data immidiately
    without users signing in. it also allows us to later associate the
    uuid with a user account when/if the user creates an account.
    '''

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        person = get_or_create_person(request)

        request.person = person

        response = self.get_response(request)
        response.set_signed_cookie(
                'uuid',
                person.uuid,
                max_age=365 * 24 * 60 * 60,
                domain=settings.SESSION_COOKIE_DOMAIN,
                secure=settings.SESSION_COOKIE_SECURE or None
            )
        # Code to be executed for each request/response after
        # the view is called.

        return response


class ExpoLoginMiddleware(object):
    '''
    This middleware sets information to allow us to process logins from our
    expo app.
    '''

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        request.GET.urlencode()
        expo_redirect_url = request.GET.get('expo-login-url', False)
        login_uuid = request.get_signed_cookie('uuid-expo-login', None)

        response = self.get_response(request)

        if expo_redirect_url:
            if login_uuid is None:
                response.set_signed_cookie(
                    'uuid-expo-login',
                    str(uuid()),
                    max_age=120,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    secure=settings.SESSION_COOKIE_SECURE or None
                )
            cache.set(
                'EXPO-REDIRECT-URL', expo_redirect_url, 120)
            cache.set(
                'USER-LOGIN-FROM-EXPO-{0}'.format(login_uuid), 120)

        # Code to be executed for each request/response after
        # the view is called.
        return response


class LanguageMiddleware(object):
    '''
    Sets the default language for the site when a user access it.
    Nopte that in the settings we set a default language (mi), however
    we'd like to be able to switch languages based on the domain name
    without having different site IDs. Therefore we write a middleware
    that detects what domainname is being used and chooses a lanaguage
    based on that. we should probaly put that language and domainname
    dictionary in the settigns somewhere and load that up.

    '''

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        set_cookie = False
        if settings.LANGUAGE_COOKIE_NAME in request.COOKIES:
            language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        elif hasattr(request, 'user'):
            if request.user.is_authenticated:
                current_language = get_current_language(request)
                if current_language:
                    set_cookie = True
        else:

            # Choose a language ebased on the host domainname
            domain = request.META['SERVER_NAME']
            
            try:
                language = LANGUAGE_DOMAINS[domain]
            except KeyError:
                language = settings.LANGUAGE_CODE

            logger.debug('Explicitly setting language from domain: {0}:{1}'.format(domain, language))
            # language = translation.get_language()
            # set_cookie = True

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
        response = self.get_response(request)

        if set_cookie:
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                language,
                max_age=2*365 * 24 * 60 * 60,
                domain=settings.SESSION_COOKIE_DOMAIN,
                secure=settings.SESSION_COOKIE_SECURE or None
            )

        # Code to be executed for each request/response after
        # the view is called.

        # Deactivates our langauge after we've processed the request.
        # WHY?
        # translation.deactivate()  
        return response


class LicenseMiddleware(object):
    '''
    This middleware sets the license of the current site.
    '''

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        try:
            person = get_or_create_person(request)
            try:
                active = KnownLanguage.objects.get(active=True, person=person)
                license = License.objects.get(language=active.language)
            except ObjectDoesNotExist:
                license = SiteLicense.objects.get(site=get_current_site(request))
            except MultipleObjectsReturned:
                licenses = License.objects.filter(language=active.language)
                license = licenses[0]
                logger.error('MORE THAN ONE LICENSE WITH SAME LANGUAGE!')
            request.license = license
        except Exception as e:
            request.license = None

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response


def show_toolbar_callback(arg):
    if settings.DEBUG:
        return True
