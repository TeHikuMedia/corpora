# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import math
import decimal
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey,\
                                               GenericRelation
from django.contrib.contenttypes.models import ContentType

from django.contrib.postgres.indexes import BrinIndex

from django.contrib.auth.models import User
from corpus.base_settings import LANGUAGES, LANGUAGE_CODE, DIALECTS

from uuid import uuid4
import os
import hashlib

from django.utils.safestring import mark_safe


def get_md5_hexdigest_of_file(file_object):
    hash_md5 = hashlib.md5()
    close_file = False
    try:
        if file_object.closed:
            file_object.open('rb')
            close_file = True

        for chunk in iter(file_object.chunks()):
            hash_md5.update(chunk)

        if close_file:
            file_object.close()

        result = hash_md5.hexdigest()
        del hash_md5
        return result

    except IOError:
        del hash_md5
        return None


def upload_directory(instance, filename):
    d = timezone.now()
    i = str(uuid4())
    return '{0}/{1}.{2}'.format(
        d.strftime('%Y/%m/%d/%H/%M'),
        i,
        filename.split('.')[-1])


class QualityControl(models.Model):
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
    delete = models.BooleanField(
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
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        help_text='Model to which this QualityControl refers. This should be \
        the content type ID. Implemented types are Recordings (id=8),\
        Sentences (id=10), Transcription Segments (id=24).')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
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
    # recording = models.ForeignKey('corpus.Recording', null=True)

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Field for providing extra information about a review.")

    machine = models.BooleanField(
        default=False,
        help_text='Boolean to indicate if a machine made the review.')
    source = models.ForeignKey(
        'Source',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='Used to identify machines.')

    class Meta:
        unique_together = (("object_id", "content_type", "person"),)
        indexes = [
            models.Index(fields=['object_id', 'content_type', ]),
            models.Index(fields=['delete', ]),
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

    def calculate_score(self):
        """Listener/reviewer score for this review - the closer to the mean,
        the higher the score. """

        qc = QualityControl.objects.filter(content_type=self.content_type,
                                           object_id=self.object_id)
        avg = qc.aggregate(
            value=models.Avg(models.F('good') - models.F('bad')))

        # normalise to between -1 and 1 - TODO check this is correct
        avg = max(-1, min(1, avg['value'] or 0))
        vote = max(-1, min(1, self.good - self.bad))

        return 1 - decimal.Decimal(abs(vote - avg)) / 2

    def __unicode__(self):
        try:
            ct = str(self.content_type).title()
        except:
            ct = 'None'
        try:
            co = self.content_object.__unicode__()
        except:
            co = 'None'
        return u'{0}: {1}'.format(ct, co)


# class SentenceQualityControl(models.Model):

#     good = models.PositiveIntegerField(
#         default=0,
#         help_text='Indicates the object is good. Can be any interger >= 0.')
#     bad = models.PositiveIntegerField(
#         default=0,
#         help_text='Indicates the object is bad. Can be any interger >= 0.')
#     approved = models.BooleanField(
#         default=False,
#         help_text='Approved indicates that the object is suitable for use.')
#     approved_by = models.ForeignKey(
#         User, null=True, blank=True,
#         on_delete=models.SET_NULL,
#         help_text='User that approved the object. Should be a user ID.')
#     delete = models.BooleanField(
#         default=False,
#         help_text='Flag for deletion.')
#     star = models.PositiveIntegerField(
#         default=0,
#         help_text='Stars are to indicate an object is amazing. This is a positive\
#         interger field so we can, for example, do a 5 star rating system.')
#     follow_up = models.BooleanField(
#         default=False,
#         help_text='Flag an item for follow up later.')

#     updated = models.DateTimeField(auto_now=True)
#     person = models.ForeignKey('people.Person', null=True, blank=True)

#     sentence = models.ForeignKey('corpus.Sentence', null=True)

#     notes = models.TextField(
#         blank=True,
#         null=True,
#         help_text="Field for providing extra information about a review.")

#     machine = models.BooleanField(
#         default=False,
#         help_text='Boolean to indicate if a machine made the review.')

#     source = models.ForeignKey(
#         'Source',
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         help_text='Used to identify machines.')

#     class Meta:
#         unique_together = (("object_id", "content_type", "person"),)
#         indexes = [
#             models.Index(fields=['object_id', 'content_type', ]),
#             # models.Index(fields=['first_name'], name='first_name_idx'),
#         ]

#     def clear(self):
#         self.good = 0
#         self.bad = 0
#         self.approved = False
#         self.approved_by = None

#     def __unicode__(self):
#         try:
#             ct = str(self.content_type).title()
#         except:
#             ct = 'None'
#         try:
#             co = self.content_object.__unicode__()
#         except:
#             co = 'None'
#         return u'{0}: {1}'.format(ct, co)


class Source(models.Model):
    SOURCE_TYPES = (
        ('W', 'Website'),
        ('A', 'Article'),
        ('B', 'Book'),
        ('I', 'Interview'),
        ('S', 'Self'),
        ('D', 'Document'),
        ('M', 'Machine'),
    )

    description = models.TextField(
        help_text='Any extra info about the source',
        null=True,
        blank=True)
    author = models.CharField(
        help_text="Author's name",
        max_length=128,
        null=True,
        blank=True)
    source_type = models.CharField(
        max_length=1,
        choices=SOURCE_TYPES,
        null=True,
        blank=True,
        help_text='Source type is a single character.\
            Valid source types include {0}.'.format(
            ", ".join(
                ["'{0}' ({1})".format(i[0], i[1]) for i in SOURCE_TYPES]))
            )
    source_name = models.CharField(
        help_text="Name of the source",
        max_length=256,
        null=True,
        blank=True)
    added_by = models.ForeignKey(
        'people.Person',
        null=True,
        blank=True)
    source_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL for the source (e.g. a website or API endpoint).\
        This field can be None.")

    class Meta:
        verbose_name = 'Source'
        verbose_name_plural = 'Sources'
        unique_together = (
            ("source_name", "source_type", "author", 'source_url'),)

    def __unicode__(self):
        return "{0} by {1}".format(self.source_name, self.author)


class Sentence(models.Model):
    text = models.CharField(
        help_text='The sentence to be spoken.',
        max_length=1024, unique=True
        )

    language = models.CharField(
        choices=LANGUAGES,
        max_length=16,
        default=LANGUAGE_CODE
        )
    dialect = models.CharField(
        choices=DIALECTS,
        max_length=8,
        null=True,
        blank=True)

    quality_control = GenericRelation(
        QualityControl,
        related_query_name='sentence'
        )

    updated = models.DateTimeField(auto_now=True)
    source = models.ForeignKey(
        'Source',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Sentence'
        verbose_name_plural = 'Sentences'
        indexes = [
            # models.Index(fields=['quality_control'])
        ]

    def clean(self):
        if len(self.text) > 124:
            raise ValidationError('Sentence too long')

        if Sentence.objects.exclude(pk=self.pk).filter(text=self.text):
            raise ValidationError('Duplicate sentence')

    def __unicode__(self):
        return self.text

    def get_features(self):
        import features
        f = features.import_finder(self.language)
        return f(self.text)


class Recording(models.Model):
    person = models.ForeignKey(
        'people.Person',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
        )

    sentence = models.ForeignKey(
        'Sentence',
        null=True,
        on_delete=models.SET_NULL
        )

    quality_control = GenericRelation(
        QualityControl,
        related_query_name='recording'
        )

    source = models.ForeignKey(
        'Source',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)

    language = models.CharField(
        verbose_name=_('language'),
        choices=LANGUAGES,
        max_length=16,
        default=LANGUAGE_CODE,
        blank=True,
        help_text='Language for a particular recording')

    # Dialect? Add field so we can flag a dialect for a recording.
    dialect = models.CharField(
        choices=DIALECTS,
        max_length=8,
        null=True,
        blank=True,
        verbose_name=_('dialect'))

    audio_file = models.FileField(upload_to=upload_directory)
    audio_file_md5 = models.CharField(
        max_length=32, editable=False, default=None, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    sentence_text = models.CharField(max_length=250, blank=True, null=True)
    duration = models.FloatField(default=0, blank=True)

    audio_file_aac = models.FileField(
        upload_to=upload_directory, null=True, blank=True)

    audio_file_wav = models.FileField(
        upload_to=upload_directory, null=True, blank=True)
    audio_file_wav_md5 = models.CharField(
        max_length=32, editable=False, default=None, null=True)

    user_agent = models.CharField(
                        max_length=512, blank=True, null=True)

    class Meta:
        verbose_name = 'Recording'
        verbose_name_plural = 'Recordings'
        unique_together = (("person", "sentence"),)
        indexes = [
            # BrinIndex(fields=['created']),
            models.Index(fields=['-updated']),
            # models.Index(fields=['quality_control'])
        ]

    def __unicode__(self):
        try:
            return self.get_sentence_text() + u" by " + self.get_person_name()
        except:
            return self.get_sentence_text()

    def audio_file_admin(self):
        url = self.get_recording_file_url()
        return mark_safe("""
            <a href='%s'
            target="popup"
            onclick="window.open('%s','popup','width=400,height=200'); return false;"
            >%s</a>""" % (url, url, url))

    def get_recording_file_url(self):
        from django.urls import reverse
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        try:
            url = "https://{1}{0}".format(
                reverse('corpus:recording_file', kwargs={'pk': self.pk}),
                current_site.domain)
        except:
            url = ""
        return url

    def get_recording_file_name(self):
        parts = self.audio_file.name.split('.')
        parts.pop()
        return os.path.basename('.'.join(parts))

    def get_sentence_text(self):
        if self.sentence_text:
            return self.sentence_text
        elif self.sentence:
            return self.sentence.text
        else:
            return 'None'  # Some reasone making this _() causes error in admin.

    def get_person_name(self):
        if self.person:
            return self.person.full_name
        else:
            return _(u'None')

    def calculate_score(self):
        """Score awarded for uploading this recording. """

        approved = self.quality_control \
            .filter(approved=True)

        if approved.count() >= 1:
            return 1

        net_votes = self.quality_control \
            .aggregate(value=models.Sum(models.F('good') - models.F('bad')))

        net_votes = decimal.Decimal(net_votes['value'] or 0)
        damper = 4
        return max(0, 1 - math.exp(-(net_votes + 1) / damper))

    def save(self, *args, **kwargs):
        if self.audio_file is not None and self.audio_file_md5 is None:
            self.audio_file_md5 = get_md5_hexdigest_of_file(self.audio_file)

        # I really don't understand something fundamendal here! why does
        # if self.audio_file_wav is not None: not work!
        try:
            if self.audio_file_wav is not None:
                if self.audio_file_wav_md5 is None:
                    self.audio_file_wav_md5 = \
                        get_md5_hexdigest_of_file(self.audio_file_wav)
        except:
            pass

        super(Recording, self).save(*args, **kwargs)


class Text(models.Model):
    language = models.CharField(
        verbose_name=_('language'),
        choices=LANGUAGES,
        max_length=16,
        default=LANGUAGE_CODE
        )
    dialect = models.CharField(
        choices=DIALECTS,
        max_length=8,
        null=True,
        blank=True)
    updated = models.DateTimeField(verbose_name=_('updated'), auto_now=True)
    source = models.ForeignKey('Source', verbose_name=_('source'))
    uploaded_file = models.FileField(verbose_name=_('uploaded file'),
                                     upload_to='%Y/%m/%d/%H/%M',
                                     help_text=_('.txt format'))

    class Meta:
        verbose_name = _('text')
        verbose_name_plural = _('texts')

    def __unicode__(self):
        return str(self.uploaded_file)
