# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.conf import settings
from django.db.models import Q, Count
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from corpus.models import Recording, Sentence, Source
from transcription.models import \
    Transcription, TranscriptionSegment, AudioFileTranscription
from corpus.views.views import RecordingFileView
from django.contrib.sites.shortcuts import get_current_site

from corpora.utils.tmp_files import prepare_temporary_environment
from corpora.utils.task_management import \
    check_and_set_task_running, clear_running_tasks, \
    check_task_counter_running, task_counter
from corpora.utils.media_functions import get_media_duration
from people.helpers import get_current_known_language_for_person

from transcription.utils import \
    create_and_return_transcription_segments, check_to_transcribe_segment

from transcription.transcribe import \
    transcribe_audio_sphinx, transcribe_segment_async, transcribe_aft_async, \
    calculate_word_probabilities

from helpers.media_manager import MediaManager

from django.utils import timezone
from django.core.files import File
import wave
import contextlib
import os
import stat
import ast
import sys
import requests
import uuid
from subprocess import Popen, PIPE
import time

from django.core.cache import cache

import logging
logger = logging.getLogger('corpora')
logger_test = logging.getLogger('django.test')


@shared_task
def set_audiofile_duration(aft_pk):
    try:
        aft = AudioFileTranscription.objects.get(pk=aft_pk)
    except ObjectDoesNotExist:
        logger.warning('Tried to get AFT that doesn\'t exist')
        return 'Tried to get recording that doesn\'t exist'

    aft.duration = get_media_duration(aft)
    aft.save()

    return 'AFT {0} duration set to {1}'.format(aft.pk, aft.duration)


@shared_task
def launch_transcription_api():
    num_jobs = cache.get('TRANSCRIPTION_JOBS', 0)

    # logger.debug('NUM_TRANSCRIPTION_JOBS: {0: <4f}'.format(num_jobs))

    '''
    Let's check jobs every minut, and maybe have a cooldown of 5 minutes
    so the initial get re4quests cause us to ensure that we're running a server,
    but after 5 minutes if there are no actual transcription jobs then we should
    just take the servers down
    '''

    # logger.debug('LAUNCHING')
    return "DISABLED CHANGING OF AUTOSCALINGGROUP"

    import boto3
    import os
    os.environ['PROJECT_NAME']
    client = boto3.client(
        'autoscaling',
        aws_access_key_id=os.environ['AWS_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET'],
        region_name='ap-southeast-2')

    response = client.set_desired_capacity(
            AutoScalingGroupName='asg-corpora-production-deepspeech',
            DesiredCapacity=1,
            HonorCooldown=False,
        )


@shared_task
def launch_watcher():
    # Use beat to schedule this
    last_queue = cache.get('JOBS_PING', [])
    num_jobs = cache.get('TRANSCRIPTION_JOBS', 0)
    last_queue.insert(0, num_jobs)

    count = 0
    for i in range(len(last_queue)-1):
        if last_queue[i] - last_queue[i+1] == 0:
            count = count + 1

    if count == 3:
        num_jobs = 0

    last_queue = cache.set('JOBS_PING', last_queue)
    # logger.debug('NUM_TRANSCRIPTION_JOBS: {0: <4f}'.format(num_jobs))

    if num_jobs <= 0:
        logger.debug('STOPPING')

        return "DISABLED CHANGING OF AUTOSCALINGGROUP"

        client = boto3.client(
            'autoscaling',
            aws_access_key_id=os.environ['AWS_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET'],
            region_name='ap-southeast-2')

        response = client.set_desired_capacity(
                AutoScalingGroupName='asg-corpora-production-deepspeech',
                DesiredCapacity=0,
                HonorCooldown=True,
            )

@shared_task
def transcribe_all_recordings():
    MAX_LOOP = 3500
    recordings = Recording.objects\
        .filter(transcription__isnull=True)\
        .distinct().order_by('created')

    if recordings.count() == 0:
        recordings = Recording.objects\
            .filter(transcription__words__isnull=True)\
            .distinct().order_by('created')

    total = recordings.count()
    start = timezone.now()

    if total == 0:
        return "No recordings to transcribe."

    recordings = recordings[:MAX_LOOP]

    source, created = Source.objects.get_or_create(
        source_name='Transcription API',
        source_type='M',
        source_url=settings.DEEPSPEECH_URL,
        author='Keoni Mahelona'
    )
    source.save()

    error = 0
    e = 'None'
    for recording in recordings:
        t, created = Transcription.objects.get_or_create(
                recording=recording,
                source=source,
            )

    count = 0.0
    for recording in recordings:
        transcribe_recording.apply_async(
            args=[recording.pk],
        )
        count = count+1

    if total > MAX_LOOP:
        t = MAX_LOOP
        left = total - MAX_LOOP
    else:
        t = total
        left = 0

    time = timezone.now()-start
    return "Done with {0} recordings. {1} to transcribe. Took {2}s" \
        .format(recordings.count(), left, time.total_seconds())


@shared_task
def transcribe_recordings_without_reviews():
    MAX_LOOP = 3500
    recordings = Recording.objects\
        .filter(transcription__isnull=True)\
        .distinct().order_by('created')

    # Once we're done with all the recordings,
    # let's see if there are some unfinished ones.
    if recordings.count() == 0:
        recordings = Recording.objects\
            .filter(quality_control__isnull=True)\
            .filter(transcription__metadata=None)\
            .distinct().order_by('created')

    total = recordings.count()
    start = timezone.now()

    if total == 0:
        return "No recordings to transcribe."

    logger.debug('Recordings that need reviewing: {0}'.format(total))

    recordings = recordings[:MAX_LOOP]

    source, created = Source.objects.get_or_create(
        source_name='Transcription API',
        source_type='M',
        source_url=settings.DEEPSPEECH_URL,
        author='Keoni Mahelona'
    )
    source.save()

    error = 0
    e = 'None'
    for recording in recordings:
        t, created = Transcription.objects.get_or_create(
                recording=recording,
                source=source,
            )

    count = 0.0
    for recording in recordings:
        transcribe_recording.apply_async(
            args=[recording.pk],
        )
        count = count+1

    if total > MAX_LOOP:
        t = MAX_LOOP
        left = total - MAX_LOOP
    else:
        t = total
        left = 0

    time = timezone.now()-start
    return "Done with {0} recordings. {1} to transcribe. Took {2}s" \
        .format(recordings.count(), left, time.total_seconds())


@shared_task
def transcribe_recording(pk):
    recording = Recording.objects.get(pk=pk)
    try:
        transcription = Transcription.objects.get(recording=recording)
    except MultipleObjectsReturned:
        transcriptions = Transcription.objects\
            .filter(recording=recording).order_by('pk')
        transcription = transcriptions.last()
        t = transcriptions.first()
        t.delete()
    except ObjectDoesNotExist:
        source, created = Source.objects.get_or_create(
            source_name='Transcription API',
            source_type='M',
            source_url=settings.DEEPSPEECH_URL,
            author='Keoni Mahelona'
        )

        transcription, created = Transcription.objects.get_or_create(
            recording=recording,
            source=source)

    start = timezone.now()
    if not transcription.words:
        try:
            from transcription.wer.wer import word_error_rate

            # This should tell us if the file exists
            try:
                recording.audio_file_wav.open('rb')
                result = transcribe_audio_sphinx(
                    recording.audio_file_wav.read(),
                    timeout=60)
                recording.audio_file_wav.close()
            except:
                M = MediaManager(recording.audio_file)
                M.convert_to_wave()
                f = open(M.versions['wav']['file_path'], 'rb')
                result = transcribe_audio_sphinx(
                    f.read(), timeout=60)
                f.close()
                del M


            transcription.text = result['transcription'].strip()
            transcription.transcriber_log = result
            # Calculate wer
            original = recording.sentence_text.lower()

            try:
                transcription.word_error_rate = \
                    word_error_rate(
                        original,
                        transcription.text,
                        recording.language)
            except Exception as e:
                logger.error("CANT CALC WER")
                logger.error(e)
            # Store metadata
            transcription.metadata = result['metadata']

            # Calc and store word probabilities
            try:
                transcription.words = calculate_word_probabilities(transcription.metadata)
            except Exception as e:
                logger.error("CANT CALC WORDS")
                logger.error(e)

            transcription.save()
            dt = timezone.now() - start
            return "Transcribed {0} in {1}s".format(
                transcription.text, dt.total_seconds())

        except Exception as e:
            logger.error(e)
            transcription.delete()
            return str(e)
    else:
        return "Already transcribed: {0}".format(transcription.text)


@shared_task
def delete_transcriptions_for_approved_recordings():
    transcriptions = Transcription.objects\
        .filter(recording__quality_control__approved=True)
    transcriptions.delete()


@shared_task
def check_and_transcribe_blank_segments():
    '''
    We look for segments with null text and attempt to
    transcribe then. We don't do this async because it might
    clog up our queue.
    '''
    task_key = 'check_and_transcribe_blank_segs'
    if check_and_set_task_running(task_key):
        return "Task already running. Skipping this instance."

    segments = TranscriptionSegment.objects\
        .filter(Q(text__isnull=True) &
                Q(edited_by__isnull=True) &
                Q(parent__ignore=False) &
                Q(no_speech_detected=False))

    count = 0
    for segment in segments:
        logger.debug('THIS SEGMENT DID NOT TRANSCRIBE: {0}'.format(segment.pk))
        logger.debug(segment.transcriber_log)

        try:
            if 'retry' in segment.transcriber_log.keys():
                if not segment.transcriber_log['retry']:
                    continue
        except AttributeError:
            pass

        if not check_to_transcribe_segment(segment):
            continue

        if count > 25:
            return "Checked 25 segments. \
                    Reached max loop."
        transcribe_segment_async(segment.pk)
        count = count + 1

    clear_running_tasks(task_key)
    return "Checked {0} segments of {1}.".format(count, segments.count())


@shared_task
def check_and_transcribe_blank_audiofiletranscriptions():
    '''
    We look for AFTs with null segments and attempt to
    create and transcribe then.
    '''
    task_key = 'check_and_transcribe_blank_aft'
    if check_task_counter_running(task_key):
        return "Task already running. Skipping this instance."

    task_counter(task_key, 1)

    afts = AudioFileTranscription.objects\
        .annotate(num_segments=Count('transcriptionsegment'))\
        .filter(num_segments=0) \
        .order_by('?')  # This is taxing but fine for this case.

    count = 0
    errors = 0
    error_msg = []
    for aft in afts:
        try:
            # First check if segments exist?!
            # Isn't this redundant?
            # This could help if another process started creating segments.
            segs = TranscriptionSegment.objects.filter(parent=aft)
            if segs.count() == 0:
                transcribe_aft_async(aft.pk)
        except Exception as e:
            logger.error(e)
            errors = errors + 1
            error_msg.append(e)
        count = count + 1

    task_counter(task_key, -1)

    return "Processed {0} AFTs. Had {1} errors. {2}".format(
        count, errors, error_msg)


@shared_task
def calculate_wer_for_null():
    '''
    Calculates the WER for transcriptions that don't have this.
    This can be removed after a migration as this was a newly added
    field and we really only need to run this once.
    '''
    from transcription.wer.wer import word_error_rate
    trans = Transcription.objects\
        .filter(word_error_rate=None)
    logger.debug('Need to calc wer for {0} items.'.format(trans.count()))
    count = 0
    errors = 0
    for t in trans:
        # Calculate wer
        try:
            original = t.recording.sentence_text.lower()
            t.word_error_rate = \
                word_error_rate(
                    original,
                    t.text,
                    t.recording.language)
            t.save()
        except Exception as e:
            logger.error(
                'ERROR calculated wer for Transcription {0}:{1}'.format(
                    t.pk, t.text))
            logger.error(e)
            errors = errors + 1
        count = count + 1
        if count > 10000:
            return "Done with {0} calcs and {1} errors.".format(count, errors)
