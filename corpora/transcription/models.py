# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
# from corpus.models import QualityControl
from django.contrib.auth.models import User

from django.contrib.contenttypes.fields import GenericRelation

from django.contrib.postgres.fields import JSONField

from uuid import uuid4
import os


def upload_directory(instance, filename):
    d = timezone.now()
    i = str(uuid4())
    p = instance.uploaded_by.uuid
    return 'audio/{3}/{0}/{1}.{2}'.format(
        d.strftime('%Y/%m/%d'),
        i,
        filename.split('.')[-1],
        p)


def transcription_directory(instance, filename):
    d = timezone.now()
    i = str(uuid4())
    p = instance.uploaded_by.uuid
    return 'transcriptions/{3}/{0}/{1}.{2}'.format(
        d.strftime('%Y/%m/%d'),
        i,
        filename.split('.')[-1],
        p)


class TranscriptionQualityControl(models.Model):
    good = models.PositiveIntegerField(
        default=0,
        help_text='Indicates the object is good. Can be any interger >= 0.')
    bad = models.PositiveIntegerField(
        default=0,
        help_text='Indicates the object is bad. Can be any interger >= 0.')
    approved = models.BooleanField(
        default=False,
        help_text='Approved indicates that the object is suitable for use.')
    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='User that approved the object. Should be a user ID.')
    trash = models.BooleanField(
        default=False,
        help_text='Flag for deletion.')
    star = models.PositiveIntegerField(
        default=0,
        help_text='Stars are to indicate an object is amazing. This is a positive\
        interger field so we can, for example, do a 5 star rating system.')
    follow_up = models.BooleanField(
        default=False,
        help_text='Flag an item for follow up later.')
    noise = models.BooleanField(
        default=False,
        help_text='Check if an item has noise but is still intelligible.')

    updated = models.DateTimeField(auto_now=True)
    person = models.ForeignKey(
        'people.Person',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="ID of person associated with this QualityControl object.\
        For Token Authenticated API calls, passing the string 'self' instead\
        of an Integer will associate the person of the Token with this QC \
        object.")

    # Move to Recording QC
    transcription = models.ForeignKey(
        'transcription.Transcription',
        null=True,
        on_delete=models.SET_NULL,)

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Field for providing extra information about a review.")

    machine = models.BooleanField(
        default=False,
        help_text='Boolean to indicate if a machine made the review.')
    source = models.ForeignKey(
        'corpus.Source',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='Used to identify machines.')

    class Meta:
        unique_together = (("transcription", "person"),)
        indexes = [
            # models.Index(fields=['object_id', 'content_type', ]),
            models.Index(fields=['trash', ]),
            models.Index(fields=['approved', ]),
            models.Index(fields=['good', ]),
            models.Index(fields=['bad', ]),
            # models.Index(fields=['first_name'], name='first_name_idx'),
        ]

    def clear(self):
        self.good = 0
        self.bad = 0
        self.approved = False
        self.approved_by = None

    def __str__(self):
        return u'Transcription QC: {1}'.format(self.transcription.pk)


class Transcription(models.Model):
    '''
    A transcription is very specifically a machine transcription
    of a human recording. Perhaps we should have called this model
    something else but oh well.
    '''

    recording = models.ForeignKey(
        'corpus.Recording',
        on_delete=models.CASCADE)

    text = models.CharField(
        help_text='The initial transcribed text',
        max_length=1024)

    corrected_text = models.CharField(
        help_text='The corrected text',
        max_length=1024,
        null=True,
        blank=True)

    updated = models.DateTimeField(auto_now=True)

    source = models.ForeignKey(
        'corpus.Source',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='The source should be the transcription API.')

    # quality_control = GenericRelation(
    #     QualityControl,
    #     related_query_name='transcription'
    #     )

    transcriber_log = JSONField(
        null=True,
        blank=True)

    word_error_rate = models.FloatField(
        default=None,
        blank=True,
        editable=False,
        null=True)

    # Need a model to store the extra metadata from the transcription
    # But we also need the nice times info
    # meta_data = models.
    # times = words and the time the start? JSON?

    metadata = JSONField(
        null=True, blank=True,
        help_text='Extra metadata returned from transcriber.')

    words = JSONField(null=True, blank=True,
        help_text='Words and their probabilities calculated from metadata.')


    class Meta:
        unique_together = (("recording", "source",),)

    # Is this still relevant?
    def clean(self):
        if len(self.text) > 124:
            raise ValidationError('Sentence too long')

        if Transcription.objects.exclude(pk=self.pk).filter(text=self.text):
            raise ValidationError('Duplicate sentence')

    def __str__(self):
        return self.text

    # Language and dialect should come from the recording object.


class TranscriptionSegment(models.Model):
    '''
    This model manages shorter segments of the AudioFileTranscription
    Model.
    '''

    parent = models.ForeignKey(
        'AudioFileTranscription',
        null=True,
        on_delete=models.CASCADE)

    child = models.ForeignKey(
        'Transcription',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='We can create a transcription with a recording from a segment.')

    start = models.PositiveIntegerField(
        help_text='Start time in hundreths of a second for audio segment',
        editable=False)

    end = models.PositiveIntegerField(
        help_text='End time in hundreths of a second for audio segment',
        editable=False)

    text = models.CharField(
        help_text='The initial transcribed text',
        max_length=1024,
        null=True,
        blank=True)

    corrected_text = models.CharField(
        help_text='The corrected text',
        max_length=1024,
        null=True,
        blank=True)

    source = models.ForeignKey(
        'corpus.Source',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='The source should be the transcription API.')

    edited_by = models.ForeignKey(
        'people.Person',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)

    transcriber_log = JSONField(
        null=True,
        blank=True)

    no_speech_detected = models.BooleanField(
        help_text='If we get back an empty string from the ASR, we set this\
                  flag to True.',
        default=False)

    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.corrected_text is None:
            if self.text:
                self.corrected_text = self.text
        super(TranscriptionSegment, self).save(*args, **kwargs)


class AudioFileTranscription(models.Model):
    '''
    Model for transcriptions of audio files that are (and arbitrary duraion)
    seconds or longer. For shorter transcriptions, use the Transcription
    Model.
    '''
    name = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        help_text=_(
            'Name for your audio file. If this is not provided, \
            your file name will be used.'))

    audio_file = models.FileField(
        upload_to=upload_directory,
        null=True,
        blank=False,
        help_text=_('\
            Supported file extensions include\
            .aac, .mp3, .wav, .aiff, and .m4a. '))

    audio_file_aac = models.FileField(
        upload_to=upload_directory,
        null=True,
        blank=True,
        help_text=_('\
            HE-AAC encoded version of audio_file\
            for low bitrate playback.'))

    duration = models.FloatField(default=0, blank=True)

    transcription = models.TextField(
        blank=True)

    original_transcription = models.FileField(
        upload_to=transcription_directory,
        blank=True,
        max_length=254)

    uploaded_by = models.ForeignKey(
        'people.Person',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('\
            A Person ID. This field is populated automatically if\
            not provided.'))

    ignore = models.BooleanField(
        default=False,
        help_text='Help us find and ignore bad files/uploads.')

    errors = JSONField(
        help_text='Place to store any error information.',
        default=None,
        null=True)

    # duration = models.PositiveIntegerField(
    #     blank=True, null=True, editable=False)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def clean(self):
        if self.audio_file:
            parts = self.audio_file.name.split('.')
            ext = parts[-1]
            if ext not in 'aac mp3 wav aiff m4a':
                raise ValidationError(
                    'The file you uploaded is not an audio file.')
            if self.name is None:
                self.name = u"{0}".format('.'.join(parts[:-1]))
        else:
            raise ValidationError(
                'A file is required')

    class Meta:
        verbose_name = 'Audio File Transcription'
        verbose_name_plural = 'Audio File Transcriptions'

    def __str__(self):
        if self.name:
            return self.name
        return 'None'

    def get_file_name(self):
        parts = self.audio_file.name.split('.')
        parts.pop()
        return os.path.basename('.'.join(parts))


# To Do: class LongTranscription - for transcription of a very long audio.
