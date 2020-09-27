# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext as _

from django.template.context import RequestContext
from django.shortcuts import render, redirect

from django import http
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView

from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from boto.s3.connection import S3Connection

from django.conf import settings

from people.helpers import get_unknown_languages
from people.models import Group

from corpus import views
from people.helpers import get_or_create_person
from django.contrib.sites.shortcuts import get_current_site

from django.views.decorators.cache import cache_page

from corpora.mixins import SiteInfoMixin

from django.templatetags.static import static


class HomeView(SiteInfoMixin, TemplateView):
    template_name = "corpora/home.html"
    x_title = _('Kōrero Māori')
    x_description = _("Kōrero Māori is teaching computers indigenous languages.\
        We've created an open sourced web app to help indigenous\
        communities strealine their work in language revitalisation.")
    x_image = static("corpora/img/icon.png")

    def get_context_data(self, **kwargs):
        context = super(
            HomeView, self).get_context_data(**kwargs)
        groups = Group.objects.all().order_by('name')
        context['groups'] = groups
        context['languages'] = get_unknown_languages(None)
        return context


def home(request):
    # if request.user.is_authenticated:
    #     return redirect('people:profile')
    # else:
    groups = Group.objects.all().order_by('name')
    site = get_current_site(request)
    context = {
        'request': request,
        'groups': groups,
        'languages': get_unknown_languages(None),
        'x_title': site.name,
        'x_description': _("Kōrero Māori is teaching computers indigenous languages.\
            We've created an open sourced web app to help indigenous\
            communities strealine their work in language revitalisation."),
    }

    return render(request, 'corpora/home.html', context)
    # return redirect('account/login')


def privacy(request):
    site = get_current_site(request)
    context = {
        'request': request,
        'languages': get_unknown_languages(None),
        'site': site,
        'x_title': _('Privacy Policy'),
        'x_description': _("Privacy policy for this website."),
    }

    return render(request, 'corpora/privacy.html', context)


def rules(request):
    site = get_current_site(request)

    person = get_or_create_person(request)

    if hasattr(person, 'groups'):
        groups = person.groups
        if groups.count() == 1:
            group = groups.first()
            person.group = group

    context = {
        'person': person,
        'request': request,
        'languages': get_unknown_languages(None),
        'site': site,
        'x_title': _('Rules'),
        'x_description': _("Rules for our competitions."),
    }

    return render(request, 'people/competition/rules.html', context)


# ### NOT YET IMPLEMENTED ###
class AudioileView(RedirectView):
    '''
    This class enables us to get s3 protected files.
    '''
    permanent = False

    def get_redirect_url(self, **kwargs):
        s3 = S3Connection(settings.AWS_ACCESS_KEY_ID_S3,
                          settings.AWS_SECRET_ACCESS_KEY_S3,
                          is_secure=True)
        # Create a URL valid for 60 seconds.
        return s3.generate_url(60, 'GET',
                               bucket=settings.AWS_STORAGE_BUCKET_NAME,
                               key=kwargs['filepath'])

    def get(self, request, *args, **kwargs):
        m = get_object_or_404(Recording, pk=kwargs['pk'])
        u = request.user
        p = get_or_create_person(request)

        audio_file = m.audio_file

        f = request.GET.get('format', 'aac')
        if f in 'wav':
            if m.audio_file_wav:
                audio_file = m.audio_file_wav
        else:
            if m.audio_file_aac:
                audio_file = m.audio_file_aac

        key = '{0}:{0}:listen'.format(p.uuid, m.id)
        access = cache.get(key)
        # logger.debug('CAN VIEW:  {0} {1}'.format(key, access))

        if (u.is_authenticated and u.is_staff) or (p == m.person) or (access):
            try:
                url = audio_file.path
                url = audio_file.url
            except:
                try:
                    url = self.get_redirect_url(filepath=audio_file.name)
                except:
                    url = audio_file.url

            if url:
                if self.permanent:
                    return http.HttpResponsePermanentRedirect(url)
                else:
                    return http.HttpResponseRedirect(url)
            else:
                logger.warning('Gone: %s', self.request.path,
                               extra={
                                'status_code': 410,
                                'request': self.request
                               })
                return http.HttpResponseGone()
        else:
            raise http.Http404


def health_check(request):
    return HttpResponse('kia ora')
