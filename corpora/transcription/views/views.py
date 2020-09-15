# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext as _

from django.shortcuts import render, redirect
from django.template.context import RequestContext
from django.forms import modelform_factory
from django.http import HttpResponse
from django.urls import reverse, resolve
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import json

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.contrib.contenttypes.models import ContentType

from people.models import Person, KnownLanguage
from people.helpers import get_person
from django.conf import settings

from django import http
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from boto.s3.connection import S3Connection

from django.db.models import Sum, Count, When, Value, Case, IntegerField, Q
from django.core.cache import cache

from corpus.aggregate import get_num_approved, get_net_votes

from corpora.mixins import SiteInfoMixin

from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.mixins import UserPassesTestMixin

from transcription.models import AudioFileTranscription, TranscriptionSegment

from rest_framework.authtoken.models import Token
from people.views.stats_views import JSONResponseMixin

from transcription.tasks import launch_transcription_api

from django.templatetags.static import static

import logging
logger = logging.getLogger('corpora')


# def submit_recording(request):
#     return render(request, 'corpus/submit_recording.html')


# def failed_submit(request):
#     return render(request, 'corpus/failed_submit.html')


# def record_redirect(request):
#     return redirect(reverse('corpus:record'))


class EnsureDeepSpeechRunning(object):

    def launch_ds(self):
        pass
        # launch_transcription_api.apply_async()

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            self.launch_ds()
        return super(EnsureDeepSpeechRunning, self).get(request, **kwargs)


class DashboardView(
        EnsureDeepSpeechRunning,
        SiteInfoMixin,
        UserPassesTestMixin,
        TemplateView):
    x_description = _('Reo API Dashboard')
    x_title = _('Dashboard')
    template_name = "transcription/dashboard.html"
    x_image = static("reo_api/img/icon.png")

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(
            DashboardView, self).get_context_data(**kwargs)
        person = get_person(self.request)

        try:
            token = Token.objects.get(user=person.user)
            context['token'] = token.key
        except ObjectDoesNotExist:
            pass

        return context


class TranscribeView(
        EnsureDeepSpeechRunning,
        SiteInfoMixin,
        UserPassesTestMixin,
        TemplateView):
    x_description = _('Try the speech recognizer!')
    x_title = _('Kōrero Demo')
    template_name = "transcription/speak.html"
    x_image = static("reo_api/img/icon.png")

    def test_func(self):

        return self.request.user.is_authenticated

        # key = self.request.GET.get('key', '')

        # if key == '720031ba-4db3-11e8-88f9-8c8590055544':
        #     return True

        # return self.request.user.is_staff


class TranscribeView2(
        EnsureDeepSpeechRunning,
        SiteInfoMixin,
        UserPassesTestMixin,
        TemplateView):
    x_description = _('Try the speech recognizer!')
    x_title = _('Kōrero Demo')
    template_name = "transcription/speak_new.html"
    x_image = static("reo_api/img/icon.png")

    def test_func(self):

        return self.request.user.is_authenticated

        # key = self.request.GET.get('key', '')

        # if key == '720031ba-4db3-11e8-88f9-8c8590055544':
        #     return True

        # return self.request.user.is_staff


class ReviewView(
        EnsureDeepSpeechRunning,
        SiteInfoMixin,
        UserPassesTestMixin,
        TemplateView):
    x_description = _('Review API and Data')
    x_title = _('Kōrero Māori Review for Admins')
    template_name = "transcription/review.html"
    x_image = static("reo_api/img/icon.png")

    def test_func(self):
        return (
            self.request.user.is_authenticated and self.request.user.is_staff)

    def get_context_data(self, **kwargs):
        context = super(
            ReviewView, self).get_context_data(**kwargs)
        person = get_person(self.request)

        try:
            token = Token.objects.get(user=person.user)
            context['token'] = token.key
        except ObjectDoesNotExist:
            pass

        return context


class AudioFileTranscriptionView(
        EnsureDeepSpeechRunning,
        SiteInfoMixin, UserPassesTestMixin, DetailView):
    x_description = _('Edit your transcription.')
    x_title = _('Edit Transcription')
    x_image = static("reo_api/img/icon.png")
    model = AudioFileTranscription
    context_object_name = 'aft'
    template_name = 'transcription/audio_file_transcription_detail.html'

    def test_func(self):
        person = get_person(self.request)
        aft = self.get_object()

        key = self.request.GET.get('key', '')

        if key == '720031ba-4db3-11e8-88f9-8c8590055544':
            return True

        if self.request.user.is_staff:
            return True
        else:
            return person == aft.uploaded_by

    def get_object(self, queryset=None):
        aft = super(AudioFileTranscriptionView, self).get_object(queryset)
        self.x_title = 'Edit: {0}'.format(aft.name)
        return aft

    def get_context_data(self, **kwargs):
        context = super(
            AudioFileTranscriptionView, self).get_context_data(**kwargs)

        segments = TranscriptionSegment.objects\
            .filter(parent=context['aft'])\
            .order_by('start')

        context['segments'] = segments

        return context


class AudioFileTranscriptionListView(
        EnsureDeepSpeechRunning,
        SiteInfoMixin, UserPassesTestMixin, ListView):
    x_description = _('List of your transcriptions.')
    x_title = _('Transcriptions')
    x_image = static("reo_api/img/icon.png")
    model = AudioFileTranscription
    context_object_name = 'transcriptions'
    template_name = 'transcription/audio_file_transcription_list.html'
    paginate_by = 15

    def get_queryset(self):
        person = get_person(self.request)
        qs = AudioFileTranscription.objects\
            .filter(uploaded_by=person)\
            .order_by('-updated')
        # .annotate(num_segments=Count('transcriptionsegment'))\ => takes too
        # long instead maybe we should delete the "quick test recordings" or
        # better yet just store them as anonuymous data if we *really* want to
        # keep it .filter(num_segments__gte=1)\ => prevents us from showing
        # fresh aft
        return qs

    def test_func(self):
        return self.request.user.is_authenticated

        key = self.request.GET.get('key', '')

        if key == '720031ba-4db3-11e8-88f9-8c8590055544':
            return True

        return self.request.user.is_staff
