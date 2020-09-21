# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from corpus.base_settings import LANGUAGES, LANGUAGE_CODE, DIALECTS, ACCENTS
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import uuid


def get_uuid():
    return str(uuid.uuid4())


class Tribe(models.Model):
    name = models.CharField(
        _('name'),
        help_text=_('Name of tribe.'),
        max_length=200,
        unique=True,
        )

    class Meta:
        verbose_name = _('Tribe')
        verbose_name_plural = _('Tribes')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        )

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   editable=False)
    score = models.PositiveIntegerField(
        editable=False,
        default=0)

    num_recordings = models.PositiveIntegerField(
        editable=False,
        default=0)

    duration = models.FloatField(
        default=0, blank=True, editable=False)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        indexes = [
            models.Index(fields=['-score']),
            models.Index(fields=['num_recordings']),
            models.Index(fields=['duration'])
        ]


class Person(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    full_name = models.CharField(
        help_text=_('Full Name'),
        max_length=200,
        blank=True,
        verbose_name=_('full name'))

    uuid = models.CharField(
        max_length=64,
        default=get_uuid,
        editable=False,
        unique=True)

    profile_email = models.EmailField(
        blank=True,
        null=True,
        help_text="This is a placeholder for users that don't sign up.")
    # accept_terms = models.BooleanField(editable=False, default=False)

    username = models.CharField(
        max_length=254,
        help_text=_('Username - this will be publicly viewable'),
        blank=True,
        null=True)

    receive_weekly_updates = models.BooleanField(
        default=True,
        help_text="Check to get weekly updates on your progress.")

    receive_daily_updates = models.BooleanField(
        default=True,
        help_text="Check to get daily updates on your progress.")

    receive_feedback = models.BooleanField(
        default=False,
        help_text="Check to receive feedback on your recordings in your progress reports.")

    leaderboard = models.BooleanField(
        default=True,
        help_text="Check to show your progress on the leaderboard.",
        verbose_name="Show me on the leaderboard")

    on_board = models.BooleanField(
        default=True,
        help_text="Flag to dertmine whether to show an intro.")

    just_signed_up = models.BooleanField(
        default=False,
        help_text="Flag to track when an account is created",
        editable=True)

    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text=_('Choose a group, or enter a group name to create a new one.'))

    num_recordings = models.PositiveIntegerField(
        editable=False,
        default=0)

    num_reviews = models.PositiveIntegerField(
        editable=False,
        default=0)

    num_recordings_comp = models.PositiveIntegerField(
        editable=False,
        default=0)

    num_reviews_comp = models.PositiveIntegerField(
        editable=False,
        default=0)

    score = models.PositiveIntegerField(
        editable=False,
        default=0)

    score_comp = models.PositiveIntegerField(
        editable=False,
        default=0)

    last_user_agent = models.CharField(
                        max_length=512, blank=True, null=True)

    def email(self):
        if self.user:
            return self.user.email
        else:
            return self.profile_email

    def get_username(self):
        if self.username is None:
            if self.user:
                return self.user.username
            else:
                return 'Anonymous Kumara'
        return self.username

    def get_name(self):
        if self.full_name is None:
            return self.get_username()
        else:
            return self.full_name

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')
        indexes = [
            models.Index(fields=['-score']),
            models.Index(fields=['score_comp'])
        ]

    def __unicode__(self):
        return self.full_name

    def __str__(self):
        return self.full_name


class Demographic(models.Model):
    SEX_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
        ('TF', _('Transexual (Male to Female)')),
        ('TM', _('Transexual (Female to Male)')),
    )

    age = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_('How old are you?'),
        verbose_name=_('age'))

    gender = models.CharField(
        _('gender'),
        help_text=_('Gender'),
        choices=SEX_CHOICES,
        max_length=2,
        null=True,
        blank=True,
        )

    person = models.OneToOneField(
        Person,
        related_name='demographic',
        on_delete=models.CASCADE,
        null=True,
        unique=True,
        verbose_name=_('person'))

    tribe = models.ManyToManyField(
        Tribe,
        help_text=_('Which tribe(s) do you identify with?'),
        blank=True,
        verbose_name=_('tribe'))
    # tribe - This should be many field - many to many?
    # where did you grow up
    # ethnicities
    # anthing else?

    class Meta:
        verbose_name = _('Demographic')
        verbose_name_plural = _('Demographics')

    def tribe_names(self):
        return u', '.join([a.name for a in self.tribe.all()])
    tribe_names.short_description = _('Tribes')


class KnownLanguage(models.Model):
    PROFICIENCIES = (
            (1, _('Native Speaker - Beginner')),
            (2, _('Native Speaker - Intermediate')),
            (3, _('Native Speaker - Advanced')),
            (4, _('Near Native Speaker - Beginner')),
            (5, _('Near Native Speaker - Intermediate')),
            (6, _('Near Native Speaker - Advanced')),
            (7, _('Second Language Learner - Beginner')),
            (8, _('Second Language Learner - Intermediate')),
            (9, _('Second Language Learner - Advanced')),
        )

    language = models.CharField(
        choices=LANGUAGES,
        max_length=16,
        verbose_name=_('language'))

    level_of_proficiency = models.IntegerField(
        choices=PROFICIENCIES,
        null=True,
        blank=True,
        verbose_name=_('level of proficiency'))

    person = models.ForeignKey(
        Person,
        related_name='known_languages',
        on_delete=models.CASCADE,
        verbose_name=_('person'))

    active = models.BooleanField(default=False)

    accent = models.CharField(
        choices=ACCENTS,
        max_length=8,
        null=True,
        blank=True,
        verbose_name=_('accent'))

    dialect = models.CharField(
        choices=DIALECTS,
        max_length=8,
        null=True,
        blank=True,
        verbose_name=_('dialect'))
    # where did you learn your reo?

    class Meta:
        unique_together = (('person', 'language'))
        verbose_name = _('known language')
        verbose_name_plural = _('known languages')


@receiver(models.signals.post_save, sender=KnownLanguage)
def deactivate_other_known_languages_when_known_language_activated(
        sender,
        instance,
        **kwargs):

    if instance.active:
        known_languages = KnownLanguage.objects\
            .filter(person=instance.person)\
            .exclude(pk=instance.pk)

        for kl in known_languages:
            kl.active = False
            kl.save()

# This causes a headache?
# @receiver(models.signals.post_save, sender=KnownLanguage)
# def ensure_a_language_is_active(sender, instance, **kwargs):
#     active_language = KnownLanguage.objects.filter(
#         person=instance.person,
#         active=True)

#     if active_language.count() == 0:
#         known_language = KnownLanguage.objects\
#             .filter(person=instance.person).first()
#         if known_language:
#             known_language.active = True
#             known_language.save()


@receiver(models.signals.post_delete, sender=KnownLanguage)
def change_active_language_when_active_language_deleted(
        sender, instance, **kwargs):

    if instance.active:
        known_language = KnownLanguage.objects\
            .filter(person=instance.person).first()

        if known_language:
            known_language.active = True
            known_language.save()
