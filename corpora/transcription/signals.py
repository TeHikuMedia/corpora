# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models import signals

from transcription.models import \
    AudioFileTranscription, TranscriptionSegment

from transcription.transcribe import \
    transcribe_segment_async, transcribe_aft_async

from transcription.utils import \
    compile_aft

from corpora.utils.tasks_transcoding import transcode_audio

from corpora.celery_config import app

from django.core.cache import cache

from transcription.tasks import \
    launch_transcription_api, set_audiofile_duration

import logging
logger = logging.getLogger('corpora')


# @receiver(signals.post_save,
#           sender=TranscriptionSegment,
#           dispatch_uid='get_transcription_when_segment_created')
# def get_transcription_when_segment_created(
#         sender, instance, created, **kwargs):

#     if created:
#         logger.debug('Created {0}'.format(instance))
#         transcribe_segment_async.apply_async(
#             args=[instance.pk],
#             task_id='transcribe_segment-{0}'.format(instance.pk))

#     elif instance.text is '' or instance.text is None:
#         logger.debug('Transcribing Segment {0}'.format(instance.pk))
#         transcribe_segment_async.apply_async(
#             args=[instance.pk],
#             task_id='transcribe_segment-{0}'.format(instance.pk))

@receiver(signals.post_save, sender=AudioFileTranscription)
def query_transcription_api(
        sender, instance, created, **kwargs):

    num_jobs = cache.get('TRANSCRIPTION_JOBS', 0)
    if num_jobs < 0:
        num_jobs = 1

    if created:
        cache.set('TRANSCRIPTION_JOBS', num_jobs+1)
        # logger.debug('LAUNCHING API FOR: {0:<4f} jobs'.format(num_jobs))
        # launch_transcription_api.apply_async()
    else:
        # If self if done, then subtract from jobs
        if instance.original_transcription:
            cache.set('TRANSCRIPTION_JOBS', num_jobs-1)


@receiver(signals.post_save, sender=TranscriptionSegment)
def query_transcription_api_segment(
        sender, instance, created, **kwargs):

    num_jobs = cache.get('TRANSCRIPTION_JOBS', 0)
    if num_jobs < 0:
        num_jobs = 1

    if created:
        cache.set('TRANSCRIPTION_JOBS', num_jobs+1)
        # logger.debug('LAUNCHING API FOR: {0:<4f} jobs'.format(num_jobs))
        # launch_transcription_api.apply_async()
    else:
        # If self if done, then subtract from jobs
        if instance.text is not '':
            cache.set('TRANSCRIPTION_JOBS', num_jobs-1)


@receiver(signals.post_save, sender=AudioFileTranscription)
def encode_audio_if_not_encoded(
        sender, instance, created, **kwargs):

    if not instance.audio_file_aac:

        transcode_audio.apply_async(
            args=['transcription', 'AudioFileTranscription', instance.pk],
            task_id='aft_encode-{0}'.format(instance.pk))


@receiver(signals.post_save, sender=AudioFileTranscription)
def create_segments_and_transcribe_on_create(
        sender, instance, created, **kwargs):

    if created:
        transcribe_aft_async.apply_async(
            args=[instance.pk],
            task_id='aft_seg_tran-{0}'.format(instance.pk),
            countdown=1)


@receiver(signals.post_delete, sender=AudioFileTranscription)
def auto_delete_file_on_delete(sender, instance, **kwargs):

    if hasattr(instance, 'audio_file'):
        if instance.audio_file:
            instance.audio_file.delete(False)

    if hasattr(instance, 'audio_file_aac'):
        if instance.audio_file_aac:
            instance.audio_file_aac.delete(False)

    if hasattr(instance, 'audio_file_wav'):
        if instance.audio_file_wav:
            instance.audio_file_wav.delete(False)


# Disable this and compile on demand e.g. when they download
# the file
# @receiver(signals.post_save, sender=TranscriptionSegment)
def compile_parent_transcription(
        sender, instance, created, **kwargs):

    key = 'aft_compile-{0}'.format(instance.parent.pk)
    task_id = key
    delay = 5
    run = False
    old_task_id = cache.get(key)

    if old_task_id is None:
        run = True
        cache.set(key, task_id, delay)
    else:
        if old_task_id != task_id:
            app.control.revoke(old_task_id)
            run = True
    if run:
        compile_aft.apply_async(
            args=[instance.parent.pk],
            task_id=key,
            countdown=5)


@receiver(signals.post_save, sender=AudioFileTranscription)
def set_file_duration_on_save(sender, instance, created, **kwargs):
    if instance.audio_file:
        if instance.duration <= 0:
            set_audiofile_duration.apply_async(
                args=[instance.pk],
                task_id='set_aft_duration-{0}-{1}'.format(
                    instance.pk,
                    instance.__class__.__name__))


# ### SERIOUS ISSUE ###
# ### THIS WOULD CAUSE US TO LOSE THE FILE IN THERE'S AN ERROR ON THE SAVE ###

# @receiver(models.signals.pre_save, sender=AudioFileTranscription)
# def handle_file_change(sender, instance, **kwargs):
#     """ Handles file replacements etc.
#     """

#     # this is a new instance
#     if not instance.pk:
#         return

#     # This is an existing instance
#     elif instance.pk:
#         old_instance = AudioFileTranscription.objects.get(pk=instance.pk)

#         # with a new file
#         if instance.audio_file:
#             new_file = instance.audio_file

#             # delete the old file and keep the file name link consistency
#             old_file = old_instance.audio_file
#             if old_file != new_file:
#                 old_file.delete(False)

#         else:
#             # new file is None.
#             if old_instance.audio_file:
#                 old_instance.audio_file.delete(False)
