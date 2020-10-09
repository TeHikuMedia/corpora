# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.utils.translation import ugettext as _

from django.conf import settings
from django.utils import translation, timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum

from people.models import Person, KnownLanguage, Group
from people.helpers import get_email, set_current_language_for_person

from corpus.aggregate import build_recordings_stat_dict
from corpus.models import Recording, RecordingQualityControl

from celery.task.control import revoke, inspect

from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site

from people.competition import \
    get_competition_group_score, \
    get_competition_person_score, \
    filter_qs_for_competition, \
    get_valid_group_members, \
    get_start_end_for_competition

from django.core.cache import cache
from corpora.celery_config import app

from corpus.models import Recording

import datetime
import time
import pytz
import logging
logger = logging.getLogger('corpora')


@shared_task
def clean_empty_person_models():

    people = Person.objects\
        .filter(full_name='')\
        .filter(user__isnull=True)\
        .filter(demographic__isnull=True)\
        .filter(known_languages__isnull=True)\
        .filter(recording__isnull=True)

    count = people.count()
    if count == 0:
        logger.debug('No person models to clean')
    else:
        logger.debug('Found {0} to clean'.format(count))

    for person in people:
        person.delete()


@shared_task
def clean_empty_group_models():

    groups = Group.objects.all()

    for group in groups:
        if group.person_set.count() == 0:
            logger.debug('Removing: {0}'.format(group))
            group.delete()


@shared_task
def calculate_person_scores():

    people = Person.objects.all()

    # Notes, we calculte regardless of language!
    # That can be okay - e.g. finish one language move
    # onto another?
    for person in people:
        recordings = Recording.objects.filter(person=person)

        score = 0

        for r in recordings:
            score = score + float(r.calculate_score())

        person.score = int(score)
        person.save()

    return "Updated {0} scores".format(people.count())


@shared_task
def calculate_group_scores():

    groups = Group.objects.all()

    for group in groups:
        update_group_score(group)

    return "Updated {0} scores".format(groups.count())


@shared_task
def update_group_score(group):

    if type(group) is int:
        try:
            group = Group.objects.get(pk=group)
        except ObjectDoesNotExist:
            return "Group with pk {0} doesn't exist.".format(group)

    score, count = get_competition_group_score(group)

    group.score = int(score)
    group.num_recordings = count

    duration_qs = filter_qs_for_competition(
        Recording.objects.filter(
            person__in=get_valid_group_members(group)))
    duration = duration_qs.aggregate(total_duration=Sum('duration'))

    if duration['total_duration'] is None:
        total_duration = 0
    else:
        total_duration = duration['total_duration']

    group.duration = total_duration
    group.save()

    return "New score for {0}: {1}.".format(group.pk, group.score)


@shared_task
def update_person_score(person_pk):

    try:
        person = Person.objects.get(pk=person_pk)
    except ObjectDoesNotExist:
        return "Person with pk {0} does not exist.".format(person_pk)

    # Notes, we calculte regardless of language!
    # That can be okay - e.g. finish one language move
    # onto another?

    recordings = Recording.objects.filter(person=person)
    reviews = RecordingQualityControl.objects.filter(person=person)
    person.num_recordings = recordings.count()
    person.num_reviews = reviews.count()

    start, end = get_start_end_for_competition()
    if start is not None:
        person.num_recordings_comp = recordings.filter(
            Q(created__gte=start) &
            Q(created__lte=end)).count()
        person.num_reviews_comp = reviews.filter(
            Q(updated__gte=start) &
            Q(updated__lte=end)).count()

    score = 0

    for r in recordings:
        score = score + float(r.calculate_score())

    for q in reviews:
        score = score + float(q.calculate_score())

    person.score = score
    group = person.groups.first()
    score, num = get_competition_person_score(group, person)
    person.score_comp = score

    person.save()

    groups = person.groups.all()
    for group in groups:
        key = 'update_group_score-{0}'.format(
            group.pk)
        task_id = 'update_group_score-{0}-{1}'.format(
            group.pk, timezone.now().strftime('%H%M'))
        old_task_id = cache.get(key)
        if old_task_id is None:
            update_group_score.apply_async(
                args=[group.pk],
                task_id=task_id,
                countdown=60*5)
            cache.set(key, task_id, 60*5)
        else:
            if old_task_id != task_id:
                app.control.revoke(old_task_id)
                update_group_score.apply_async(
                    args=[group.pk],
                    task_id=task_id,
                    countdown=60*5)
            else:
                pass

    return "New score for {0}: {1}".format(person_pk, score)


@shared_task
def send_person_emails_staff(frequency='weekly'):
    '''Send an email to all staff. This is being implemented for testing
    purposes but also so we can send different emails to staff with different
    priviledges'''

    people = Person.objects\
        .filter(user__is_staff=True)\
        .filter(**{'receive_{0}_updates'.format(frequency): True})

    count = 0
    for person in people:
        if settings.DEBUG:
            p_display = "{0}{1}".format(person.pk, person.profile_email)
        else:
            p_display = person.pk
        result = send_status_email.apply_async(
            args=[person.pk, frequency],
            countdown=count*2,
            task_id='send_{1}_email-staff-{0}-{2}'.format(
                p_display, frequency, timezone.now().strftime("%y%m%d-%H%M%S"))
            )
        count = count+1
        logger.debug("Sending email to {0}".format(person))
    return "Sent emails to {0} staff.".format(count)


@shared_task
def send_person_emails_weekly():
    send_person_emails.apply_async(
        args=['weekly'])


@shared_task
def send_person_emails_daily():
    send_person_emails.apply_async(
        args=['daily'])


@shared_task
def send_person_emails(frequency='weekly'):
    '''Send a email to all people.'''

    counter = 0
    # Check if site is development
    if settings.DEBUG:
        send_person_emails_staff.apply_async(
            args=[frequency],
            countdown=2)
        return "This is a dev environment!"
    else:

        people = Person.objects.filter(
            **{'receive_{0}_updates'.format(frequency): True})
        for person in people:
            email = get_email(person)
            if email:
                try:
                    logger.debug("Sending email to {0}".format(person))
                    result = send_status_email(person.pk, frequency)
                    time.sleep(.33)
                    logger.debug(result)
                    counter = counter + 1
                except:
                    logger.debug("Email did not send for {0}".format(person))

    return "Sent {0} {1} emails.".format(counter, frequency)


@shared_task
def send_status_email(person_pk, frequency='weekly'):
    from corpora.email_utils import EMail

    try:
        person = Person.objects.get(pk=person_pk)
    except ObjectDoesNotExist:
        return "No person with id {0} found.".format(person_pk)

    # Set the language - this is used when rendering the templates.
    language = translation.get_language()
    try:
        active_language = \
            KnownLanguage.objects.get(person=person, active=True)
        language = active_language.language
    except ObjectDoesNotExist:
        pass
    translation.activate(language)

    recordings = Recording.objects.all()
    stats = build_recordings_stat_dict(recordings)
    total_seconds = stats['total_seconds']
    hours = total_seconds/60.0/60.0

    recordings = recordings.filter(person=person)
    stats = build_recordings_stat_dict(recordings)

    if 'daily' in frequency:
        time_delta = datetime.timedelta(days=1)
        period_of_time = _('today')
        previous_period_of_time = _('yesterday')

        this_period_dt = \
            timezone.localize(
                datetime.datetime.combine(
                timezone.now(),
                datetime.time())
                )

        last_period_dt = \
            this_period_dt-time_delta

    else:
        time_delta = datetime.timedelta(days=7)
        period_of_time = _('this week')
        previous_period_of_time = _('last week')

        now = timezone.now()
        week_day = now.weekday()

        this_period_dt = \
            datetime.datetime.combine(
                timezone.now()-datetime.timedelta(days=week_day),
                datetime.time())

        last_period_dt = \
            this_period_dt-time_delta

    period = recordings.filter(created__gt=this_period_dt)
    this_period_stats = build_recordings_stat_dict(period)

    period = recordings\
        .filter(created__lte=this_period_dt)\
        .filter(created__gt=last_period_dt)
    last_period_stats = build_recordings_stat_dict(period)

    lastest_recording = recordings\
        .order_by('-created')\
        .first()

    if lastest_recording is None:
        # User hans't even recorded anything,
        # so no point sending emails.
        return "Not sending status email since {0} hasn't \
                recorded anything in a while.".format(person.pk)

    if lastest_recording.created < last_period_dt:
        # The user hasn't recorded anythign in ages.
        # Let's turn this off!
        return "Not sending status email since {0} hasn't \
                recorded anything in a while.".format(person.pk)

    # approval_rate =

    email = get_email(person)

    if email:

        url_append = 'https://' + Site.objects.get_current().domain

        subject = "Your {0} update!".format(frequency)

        e = EMail(to=email, subject=subject)
        context = {
            'subject': subject,
            'person': person,
            'stats': stats,
            'this_period_stats': this_period_stats,
            'last_period_stats': last_period_stats,
            'total_duration': "{0:.1f}".format(hours),
            'url_append': url_append,
            'site': Site.objects.get_current(),
            'period_of_time': period_of_time,
            'previous_period_of_time': previous_period_of_time,
            'frequency': frequency}

        e.text('people/email/freq_stats_update.txt', context)
        e.html('people/email/freq_stats_update.html', context)

        if settings.DEBUG:
            p_display = email
        else:
            p_display = person_pk

        try:
            result = e.send(
                from_addr='Kōrero Māori <koreromaori@tehiku.nz>',
                fail_silently='False')
        except Exception as e:
            result = 10
            pass

        if result == 1:
            return "Sent email to {0}".format(p_display)
        else:
            return \
                "Error sending email to {0} - {1}.".format(p_display, result)

    else:
        return "No email associated with person."
