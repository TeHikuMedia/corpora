# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext as _

from django.shortcuts import render, redirect
from django.template.context import RequestContext
from django.forms import modelform_factory
from django.http import HttpResponse
from django.urls import reverse, resolve
from django.core.exceptions import ValidationError
import json
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.contrib.contenttypes.models import ContentType

from corpus.models import Recording, Sentence, \
    RecordingQualityControl, SentenceQualityControl

from people.models import Person, KnownLanguage
from corpus.helpers import get_next_sentence
from people.helpers import get_or_create_person, get_person, get_current_language
from django.conf import settings

from django import http
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from boto.s3.connection import S3Connection

from django.db.models import Sum, Count, When, Value, Case, IntegerField, Q
from django.core.cache import cache

from corpus.aggregate import get_num_approved, get_net_votes

from corpora.mixins import SiteInfoMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from django.views.decorators.csrf import ensure_csrf_cookie

import json

from django.templatetags.static import static

import logging
logger = logging.getLogger('corpora')


class SentenceListView(
        SiteInfoMixin, ListView):
    model = Sentence
    x_description = _('Approve sentences to use when gathering recordings.')
    x_title = _('Sentences')

    def get(self, request, *args, **kwargs):
        self.request = request
        return super(SentenceListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SentenceListView, self).get_context_data(**kwargs)
        user = self.request.user
        person = get_person(self.request)
        user.can_approve = user.is_staff and user.is_authenticated
        ct = ContentType.objects.get(model='sentence')
        context['content_type'] = ct.id
        context['user'] = user
        context['person'] = person
        context['uuid'] = self.request.get_signed_cookie('uuid', 'none')
        return context


def submit_recording(request):
    return render(request, 'corpus/submit_recording.html')


def failed_submit(request):
    return render(request, 'corpus/failed_submit.html')


def record_redirect(request):
    return redirect(reverse('corpus:record'))


class RecordView(
        SiteInfoMixin, TemplateView):
    '''
    TODO: Move RECORD to a class view
    '''

    x_title = _('Record'),
    x_description = _('Help us teach computers the sounds\
        of a language by reading sentences.')
    x_image = static("corpora/img/icon.png")

    pass


@ensure_csrf_cookie
def record(request):
    # Get the person object from the user

    # if not request.user.is_authenticated:
    # return redirect(reverse('account_login'))

    person = get_or_create_person(request)

    # if request.method == 'GET':
    #     if request.GET.get('sentence', None):
    #         sentence = Sentence.objects.get(pk=request.GET.get('sentence'))
    #     else:
    #         sentence = get_next_sentence(request)
    #         if sentence is None:
    #             return redirect('people:profile')

    # Generate a form model from the Recording model
    RecordingFormAJAX = modelform_factory(Recording, fields='__all__')

    # If page receives POST request, save the submitted audio data as a
    # recording model
    if request.method == 'POST' and request.is_ajax():

        # Create a form from the Recording Form model
        form = RecordingFormAJAX(request.POST, request.FILES)

        # If the form is valid, save the new model and send back an OK HTTP
        # Response
        if form.is_valid():
            recording = form.save()
            recording.save()
            return HttpResponse(
                json.dumps({
                    'success': True,
                    'message': "Thank you for submitting a recording!\
                                Here's another sentence for you to record.",
                    'recording': json.dumps(
                        {'id': recording.id,
                         'sentence_text': recording.sentence_text})
                }),
                content_type='application/json',
            )

        # If the form is not valid, sent a 400 HTTP Response
        else:
            errors = form.errors
            response = HttpResponse(
                json.dumps({
                        'err': "Sorry, your recording did not save.",
                        'result': json.dumps(errors)
                    }),
                content_type='application/json'
            )
            response.status_code = 400

            return response

    # Load up the page normally with request and object context

    request.user.can_approve = request.user.is_staff and \
        request.user.is_authenticated

    ct = ContentType.objects.get(model='sentence')

    context = {'request': request,
               'person': person,
               # 'sentence': sentence,
               'content_type': ct.id,
               'user': request.user,
               'uuid': request.get_signed_cookie('uuid', 'none'),
               'show_stats': True,
               'x_title': _('Record'),
               'x_description': _('Help us teach computers the sounds of a language by reading sentences.'),
               'x_image': static("corpora/img/icon.png")
               }

    response = render(request, 'corpus/record.html', context)
    response.set_signed_cookie('uuid', person.uuid, max_age=60*60*24*365)

    return response


class RecordingFileView(RedirectView):
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
        p = get_person(request)

        rType = request.GET.get('json', False)
        audio_file = m.audio_file

        f = request.GET.get('format', 'aac')
        if f in 'wav':
            if m.audio_file_wav:
                audio_file = m.audio_file_wav
            else:
                # Let's try to create the wave file
                from corpus.tasks import encode_audio
                result = encode_audio(m, codec='wav')
                if m.audio_file_wav:
                    audio_file = m.audio_file_wav
        else:
            if m.audio_file_aac:
                audio_file = m.audio_file_aac

        if p is not None:
            uuid = p.uuid
        else:
            uuid = 'None-Person-Object'
        key = '{0}:{1}:listen'.format(uuid, m.id)
        access = cache.get(key)
        logger.debug('   CAN VIEW: {0} {1}'.format(key, access))


        url = ''
        if (u.is_authenticated and u.is_staff) or (p == m.person) or (access):
            
            # This code in mental!
            try:
                url = audio_file.path
                url = audio_file.url
            except:
                try:
                    url = self.get_redirect_url(filepath=audio_file.name)
                except:
                    url = audio_file.url
            if 'http' not in url:
                url = 'https://'+ request.META['HTTP_HOST']+ url
            logger.debug(url)
            if url:
                if rType:
                    if 'http' not in url:
                        pass
                    return http.HttpResponse(
                        json.dumps({'url': url}),
                        content_type="application/json")

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
            if rType:
                return http.HttpResponse(
                        json.dumps({'error': 'Access denied.'}),
                        content_type="application/json")
            raise http.Http404


class StatsView(SiteInfoMixin, ListView):
    model = RecordingQualityControl
    x_title = _('Stats')
    x_description = _('Statistics for all data.')

    def get_context_data(self, **kwargs):
        context = super(StatsView, self).get_context_data(**kwargs)
        user = self.request.user

        language = get_current_language(self.request)

        # qc = self.get_queryset()
        # qc_s = qc.filter(content_type='sentence')
        # qc_r = qc.filter(content_type='recording')

        sentences = Sentence.objects.filter(language=language)
        recordings = Recording.objects.filter(sentence__language=language)
        people = Person.objects.all()

        length = Recording.objects.aggregate(Sum('duration'))

        approved_sentences = sentences.filter(quality_control__approved=True)
        approved_recordings = recordings.filter(quality_control__approved=True)

        seconds = float(length['duration__sum'])
        hours = int(seconds/(60.0*60))
        minutes = int((seconds - (60*60.0)*hours)/60.0)
        seconds = int(seconds - (60*60.0)*hours - 60.0*minutes)

        recording_votes = get_net_votes(recordings)
        sentence_votes = get_net_votes(sentences)

        stats = {'recordings': {
                    'total': recordings.count(),
                    'num_approved': get_num_approved(recordings),
                    'up_votes': recording_votes[0],
                    'down_votes': recording_votes[1],
                    'duration': "{:02d}:{:02d}:{:02d} ".format(hours, minutes, seconds),
                    },
                 'sentences': {
                    'total': sentences.count(),
                    'num_approved': get_num_approved(sentences),
                    'up_votes': sentence_votes[0],
                    'down_votes': sentence_votes[1],
                    },
                 }

        stats_by_proficiency = {}
        for level in KnownLanguage.PROFICIENCIES:
            query = recordings\
                .filter(person__known_languages__language=language)\
                .filter(person__known_languages__level_of_proficiency=level[0])
            recording_votes = get_net_votes(query)
            length = query.aggregate(Sum('duration'))
            if length['duration__sum'] is None:
                seconds = 0
            else:
                seconds = float(length['duration__sum'])
            hours = int(seconds/(60.0*60))
            minutes = int((seconds - (60*60.0)*hours)/60.0)
            seconds = int(seconds - (60*60.0)*hours - 60.0*minutes)
            stats_by_proficiency[level[0]] = {
                'language_level': str(level[1]),
                'total': query.count(),
                'num_approved': get_num_approved(query),
                'up_votes': recording_votes[0],
                'down_votes': recording_votes[1],
                'duration': "{:02d}:{:02d}:{:02d} ".format(hours, minutes, seconds)
            }

        context['user'] = user
        context['num_recordings'] = recordings.count()
        context['stats'] = stats
        context['num_sentences'] = sentences.count()
        context['approved_sentences'] = approved_sentences.count()
        context['total_duration'] = "{:02d}:{:02d}:{:02d} ".format(hours, minutes, seconds)
        context['recordings_by_proficiency'] = stats_by_proficiency
        return context


def listen_redirect(request):
    return redirect(reverse('corpus:listen'))


class ListenView(SiteInfoMixin, TemplateView):
    template_name = "corpus/listen.html"
    x_title = _('Listen')
    x_description = _('Listen to and vote on recordings. This helps us improve\
the quality of recordings we use.')

    def get_context_data(self, **kwargs):
        context = super(ListenView, self).get_context_data(**kwargs)
        user = self.request.user
        person = get_or_create_person(self.request)

        # Don't fech recordings the person already listened to
        recordings = Recording.objects\
            .exclude(quality_control__person=person)\
            .annotate(num_qc=Count('quality_control'))\
            .order_by('num_qc')

        ct = ContentType.objects.get(model='recording')
        user.can_review = False
        user.can_approve = False
        if user.is_staff and user.is_authenticated:
            user.can_approve = True
        elif user.has_perms([
                'corpus.add_recording',
                'corpus.change_recording',
                'corpus.delete_recording']):
            user.can_review = True

        if user.can_approve:
            kl = KnownLanguage()
            level_of_proficiency_display = kl.PROFICIENCIES
            context['proficiency_display'] = level_of_proficiency_display
        context['content_type'] = ct.id
        context['user'] = user
        context['person'] = person
        context['recordings'] = recordings
        context['show_qc_stats'] = True

        return context


class PronunciationView(SiteInfoMixin, UserPassesTestMixin, TemplateView):
    template_name = "corpus/pronunciation.html"
    x_title = _('Pronunciation')
    x_description = _('Developing pronunciation...')


    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser




