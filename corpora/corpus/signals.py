from django.dispatch import receiver
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .models import (
    Sentence, Recording,
    RecordingQualityControl,
    SentenceQualityControl
)
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from corpus.tasks import (
    set_recording_length,
    transcode_audio,
    build_recording_aggregate_pk
)
from people.tasks import update_person_score
from people.models import KnownLanguage
from transcription.tasks import transcribe_recording

from corpora.celery_config import app

from django.core.cache import cache

import logging
logger = logging.getLogger('corpora')

# @receiver(models.signals.post_save, sender=Sentence)
# @receiver(models.signals.post_save, sender=Recording)
# def create_quality_control_instance_when_object_created(
#         sender, instance, **kwargs):
#     qc, created = QualityControl.objects.get_or_create(
#             object_id=instance.pk,
#             content_type=ContentType.objects.get_for_model(instance)
#         )
#     if created:
#         print("Created QC object {0}".format(qc.pk))
#     else:
#         print("QC object {0} exists".format(qc.pk))


@receiver(models.signals.pre_save, sender=Sentence)
@receiver(models.signals.pre_save, sender=Recording)
def clear_quality_control_instance_when_object_modified(
        sender, instance, **kwargs):

    if isinstance(instance, Sentence):
        try:
            old_sentence = Sentence.objects.get(pk=instance.pk)

            if not (old_sentence.text == instance.text and
                    old_sentence.language == instance.language):
                qcs = SentenceQualityControl.objects.filter(
                    sentence__pk=instance.pk,
                    )
                qcs.delete()
                # for qc in qcs:
                #     print("Clearing quality control")
                #     qc.delete()

        except ObjectDoesNotExist:
            pass

    # Clear recording QC if the sentence text was changed.
    if isinstance(instance, Recording):
        try:
            old_recording = Recording.objects.get(pk=instance.pk)

            if not (old_recording.sentence_text == instance.sentence_text):
                qc = RecordingQualityControl.objects.filter(
                    recording__pk=instance.pk,
                    )
                qc.delete()
        except ObjectDoesNotExist:
            pass


# @receiver(models.signals.pre_save, sender=Sentence)
def split_sentence_when_period_in_sentence(sender, instance, **kwargs):
    parts = instance.text.split('.')
    for i in range(1, len(parts)):
        if len(parts[i]) < 6:  # This is arbitrary
            continue
        else:
            if parts[0][-1] in '!?.;':
                instance.text = parts[0]
            else:
                instance.text = parts[0]+'.'
            new_sentence = Sentence.objects.create(
                text=parts[i]+'.',
                language=instance.language)
            print("Created {0}".format(new_sentence))


# @receiver(models.signals.pre_save, sender=Sentence)
# def prevent_sentence_from_changing_when_recordings_exist(
#         sender, instance, **kwargs):
#     recordings = Recording.objects.filter(sentence=instance)
#     if len(recordings) > 0:
#         try:
#             old_sentence = Sentence.objects.get(pk=instance.pk)
#             instance.text = old_sentence.text
#         except ObjectDoesNotExist:
#             pass


@receiver(models.signals.post_save, sender=Recording)
def set_sentence_text_when_recording_created(
        sender, instance, created, **kwargs):
    if created:
        if instance.sentence:
            instance.sentence_text = instance.sentence.text
            instance.save()


@receiver(models.signals.post_save, sender=Recording)
def set_language_when_recording_created(
        sender, instance, created, **kwargs):
    if created:
        if instance.person:
            # Get current language for person
            try:
                known_language = KnownLanguage.objects.get(
                    person=instance.person, active=True)
                instance.language = known_language.language
                instance.dialect = known_language.dialect
                instance.save()
            except ObjectDoesNotExist:
                pass

# @receiver(models.signals.post_save, sender=Recording)
# def set_upadted_when_recording_saved(
#         sender, instance, created, **kwargs):
#     instance.updated = timezone.now()
#     instance.save()


@receiver(models.signals.post_save, sender=Recording)
def set_recording_length_on_save(sender, instance, created, **kwargs):
    if not instance.person:
        p_pk = 0
    else:
        p_pk = instance.person.pk

    if instance.audio_file:

        if not created and instance.duration <= 0:
            # Encoding tasks handles duration calc.
            set_recording_length.apply_async(
                args=[instance.pk],
                task_id='set_recording_length-{0}-{1}-{2}'.format(
                    p_pk,
                    instance.pk,
                    instance.__class__.__name__)
                )

        if created or (
                not instance.audio_file_aac or not instance.audio_file_wav):

            key = u"xtrans-{0}-{1}".format(
                instance.pk, instance.audio_file.name)

            is_running = cache.get(key, False)

            if not is_running:
                logger.debug('sending transcode_audio')
                time = timezone.now()
                transcode_audio.apply_async(
                    args=[instance.pk],
                    task_id='transcode_audio-{0}-{1}-{2}'.format(
                        p_pk,
                        instance.pk,
                        time.strftime('%d%m%y%H%M%S'))
                    )

                # We need to wait for the wav file to be encoded
                # for this task to run, otherwise we need to use
                # a different method. It's probably better to
                # use the inmemory file option here if we want
                # something quick but for now this just get's
                # us a transcription quickly.
                transcribe_recording.apply_async(
                    args=[instance.pk],
                    countdown=30,
                    task_id='transcribe_audio-{0}-{1}-{2}'.format(
                        p_pk,
                        instance.pk,
                        time.strftime('%d%m%y%H%M%S'))
                    )


# This isn't correct - we want the person of the recording object of quality
# control to get a new score not the person who done the QC.
# Will need to update this later. for nwo it's ok

@receiver(models.signals.post_save, sender=RecordingQualityControl)
@receiver(models.signals.post_save, sender=Recording)
def update_person_score_when_model_saved(sender, instance, created, **kwargs):

    if not instance.person:
        return False

    if isinstance(instance, Recording):
        # Check if we actually need to update the score!
        # Really we should only update the score if the
        # recording is CREATED!
        if not created:
            return

    key = 'update_person_score-{0}'.format(
        instance.person.pk)

    now = timezone.now()
    cc = "{0}".format(now.strftime('%H%M'))

    task_id = 'update_person_score-{0}-{1}'.format(
        instance.person.pk, cc)

    old_task_id = cache.get(key)
    # First signal call
    if old_task_id is None:

        if isinstance(instance, Recording):

            update_person_score.apply_async(
                args=[instance.person.pk],
                task_id=task_id,
                countdown=60*3)

        elif isinstance(instance, RecordingQualityControl):
            recording = instance.recording

            update_person_score.apply_async(
                args=[instance.person.pk],
                task_id=task_id,
                countdown=60*3)

        cache.set(key, task_id, 60*3)

    else:

        if old_task_id != task_id:
            app.control.revoke(old_task_id)

            if isinstance(instance, Recording):

                update_person_score.apply_async(
                    args=[instance.person.pk],
                    task_id=task_id,
                    countdown=60*3)

            elif isinstance(instance, RecordingQualityControl):
                recording = instance.recording

                update_person_score.apply_async(
                    args=[instance.person.pk],
                    task_id=task_id,
                    countdown=60*3)
        else:
            pass


@receiver(models.signals.post_save, sender=RecordingQualityControl)
@receiver(models.signals.post_delete, sender=RecordingQualityControl)
def update_aggregate_data(sender, instance, created, **kwargs):
    build_recording_aggregate_pk.apply_async(
        args=[instance.recording.pk])
