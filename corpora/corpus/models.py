# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey,\
                                               GenericRelation
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from corpus.base_settings import LANGUAGES, LANGUAGE_CODE

from uuid import uuid4
import os

from django.utils.safestring import mark_safe


def upload_directory(instance, filename):
    d = timezone.now()
    i = str(uuid4())
    return '{0}/{1}.{2}'.format(
        d.strftime('%Y/%m/%d/%H/%M'),
        i,
        filename.split('.')[-1])


class QualityControl(models.Model):
    good = models.PositiveIntegerField(default=0)
    bad = models.PositiveIntegerField(default=0)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    updated = models.DateTimeField(auto_now=True)
    person = models.ForeignKey('people.Person', null=True, blank=True)

    class Meta:
        unique_together = (("object_id", "content_type", "person"),)

    def __unicode__(self):
        return "{0}:{1}:{2}".format(
            self.content_type, self.object_id, self.good-self.bad)

    def clear(self):
        self.good = 0
        self.bad = 0
        self.approved = False
        self.approved_by = None


class Source(models.Model):
    SOURCE_TYPES = (
        ('W', 'Website'),
        ('A', 'Article'),
        ('B', 'Book'),
        ('I', 'Interview'),
        ('S', 'Self'),
        ('D', 'Document'),
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
        blank=True)
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
        blank=True)

    class Meta:
        verbose_name = 'Source'
        verbose_name_plural = 'Sources'
        unique_together = (("added_by", "source_name", "source_type", "author"),)

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

    def clean(self):
        if len(self.text) > 124:
            raise ValidationError('Sentence too long')

        if Sentence.objects.exclude(pk=self.pk).filter(text=self.text):
            raise ValidationError('Duplicate sentence')

    def __unicode__(self):
        return self.text


class Recording(models.Model):
    person = models.ForeignKey(
        'people.Person',
        null=True,
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

    audio_file = models.FileField(upload_to=upload_directory)
    updated = models.DateTimeField(auto_now=True)
    sentence_text = models.CharField(max_length=250, blank=True, null=True)
    duration = models.FloatField(default=0, blank=True)
    audio_file_aac = models.FileField(
                        upload_to=upload_directory, null=True, blank=True)
    user_agent = models.CharField(
                        max_length=512, blank=True, null=True)

    class Meta:
        verbose_name = 'Recording'
        verbose_name_plural = 'Recordings'
        unique_together = (("person", "sentence"),)

    def __unicode__(self):
        return self.get_sentence_text() + " by " + self.get_person_name()

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

    def get_recordign_file_name(self):
        parts = self.audio_file.name.split('.')
        parts.pop()
        return os.path.basename('.'.join(parts))

    def get_sentence_text(self):
        if self.sentence_text:
            return self.sentence_text
        elif self.sentence:
            return self.sentence.text
        else:
            return _('None')

    def get_person_name(self):
        if self.person:
            return self.person.full_name
        else:
            return _('None')


class Text(models.Model):
    language = models.CharField(
        verbose_name=_('language'),
        choices=LANGUAGES,
        max_length=16,
        default=LANGUAGE_CODE
        )
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
