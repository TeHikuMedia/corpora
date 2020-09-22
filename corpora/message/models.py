# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from django.db import models
from ckeditor.fields import RichTextField

from django.contrib.contenttypes.fields import GenericForeignKey,\
                                               GenericRelation
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone
# Create your models here.

ACTIONS = (
    ('E', _('Email')),
    ('P', _('Popup')),
)

TARGETS = (
    ('P', 'Person'),
    )


class Message(models.Model):

    content = RichTextField()
    subject = models.CharField(
        max_length=65)

    class Meta:
        pass

    def __unicode__(self):
        return self.subject


class MessageAction(models.Model):
    publish = models.BooleanField(default=False)
    publish_date = models.DateTimeField(
        default=timezone.now)
    completed = models.BooleanField(default=False)
    action = models.CharField(choices=ACTIONS, max_length=1)
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE)
    target_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    target_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="If target id is null, all objects of target will be acted on.")
    target_object = GenericForeignKey('target_type', 'target_id')
    target_filter = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        pass

    def __unicode__(self):
        return self.message.subject
