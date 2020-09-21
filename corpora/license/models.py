# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.sites.models import Site
from django.conf import settings
from people.models import Person

from corpus.base_settings import LANGUAGES, LANGUAGE_CODE


class License(models.Model):
    license_name = models.CharField(
        max_length=250,
        help_text=_('Name of license'))
    description = models.TextField(
        help_text=_('Please provide a description of the license.'))
    license = models.TextField(
        help_text=_('The actual license text.'),
        null=True)
    license_display = models.TextField(
        help_text=_('How the license should be displayed. This field is meant\
                    to include style e.g. html.'),
        null=True)
    language = models.CharField(
        choices=LANGUAGES,
        max_length=16,
        verbose_name=_('language'),
        default=LANGUAGE_CODE,
        unique=True)

    # should the site have alink to this? or each person can choose a icense?
    # initially just have one license in the database and that's the only one
    # they can use

    def __unicode__(self):
        return self.license_name

    def __str__(self):
        return self.license_name

class AcceptLicense(models.Model):
    license = models.ManyToManyField(License)
    person = models.ForeignKey(
        Person,
        related_name='acceted_licenses',
        on_delete=models.CASCADE)

    def license_names(self):
        return ', '.join([a.license_name for a in self.license.all()])
    license_names.short_description = _('Accepted licenses')


class SiteLicense(models.Model):
    site = models.OneToOneField(
        Site,
        default=settings.SITE_ID,
        on_delete=models.CASCADE)
    license = models.ForeignKey(
        License,
        null=True,
        on_delete=models.CASCADE
    )

