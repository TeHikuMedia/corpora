# -*- coding: utf-8 -*-
from django.db.models import Sum, Case, When, Value, IntegerField
from corpus.models import Sentence, \
    RecordingQualityControl, \
    SentenceQualityControl
from people.helpers import \
    get_current_language, get_or_create_person, get_person
import random

from django.contrib.contenttypes.models import ContentType


import logging
logger = logging.getLogger('corpora')


def get_sentences(request,
                  recordings=None,
                  person=None,
                  current_language=None):
    ''' Returns sentences without recordings '''

    if person is None:
        person = get_or_create_person(request)

    if current_language is None:
        current_language = get_current_language(request)

    sentences = Sentence.objects\
        .filter(language=current_language)\
        .filter(quality_control__approved=True)

    query = sentences.filter(recording__isnull=True)

    # This creates a bad loop if only one sentence without a recording
    # only that sentence is served. Perhpas we should order by num recordings
    if query.count() > 100:
        sentences = query
    else:
        sentences = sentences\
            .exclude(recording__person=person)

    return sentences


def get_next_sentence(request, recordings=None):
    sentences = get_sentences(request, recordings)
    count = sentences.count()
    if count > 1:
        i = random.randint(0, count-1)
        return sentences[i]
    elif count == 1:
        return sentences[0]
    else:
        return None


def get_sentences_annonymous(request):
    current_language = get_current_language(request)
    sentences_without_recordings = Sentence.objects\
        .filter(language=current_language, recording__isnull=True)
    return sentences_without_recordings


def get_sentence_annonymous(request):
    sentences_without_recordings = get_sentences_annonymous(request)
    return sentences_without_recordings.first()


def approve_sentence(request, sentence):
    person = get_person(request)
    try:
        qc = SentenceQualityControl.objects.create(
            person=person,
            approved=True,
            approved_by=request.user,
            notes='Approved in bulk using the admin page.',
            sentence=sentence,
            # object_id=sentence.pk,
            # content_type=ContentType.objects.get_for_model(sentence)
        )
    except:
        return False
    return True
