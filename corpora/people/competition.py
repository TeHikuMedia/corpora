# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import math
import decimal
from celery import shared_task
from django.utils.translation import ugettext as _

from django.conf import settings
from django.utils import translation, timezone
from django.core.exceptions import ObjectDoesNotExist

from people.models import Person, KnownLanguage, Group
from people.helpers import get_email, set_current_language_for_person, email_verified

from corpus.aggregate import build_recordings_stat_dict
from corpus.models import Recording, RecordingQualityControl

from celery.task.control import revoke, inspect

from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site

from django.db.models import Sum, Count, When, Value, Case, IntegerField
from django.db.models import Q, F, ExpressionWrapper, FloatField, Avg
from django.db.models.functions import Length
from django.db.models.functions import Cast
from django.core.cache import cache

from django.utils.dateparse import parse_datetime
import pytz
import random

import logging
logger = logging.getLogger('corpora')


def get_invalid_group_members(group, queryset=None):
    '''Get person objects that won't qualify to be in a group'''

    if queryset is None:
        queryset = Person.objects.all()

    # Complex query sets on related models causing problem
    # likely because it cant handle when emailaddress is null
    # for exmple there fore i will do old fashined way.

    queryset = queryset\
        .annotate(num_groups=Count('groups', distinct=True))\
        .filter(groups=group)\

    valid_pks = []
    for p in queryset:
        # Must have a valid email address
        # Must have a username of length > 0
        # Can only belong to one group
        verified_email = email_verified(p)
        if verified_email:
            if p.num_groups == 1:
                if p.username is not None:
                    if len(p.username) > 1:
                        valid_pks.append(p.pk)

    queryset = queryset.exclude(pk__in=valid_pks)

    return queryset


def get_valid_group_members(group, queryset=None):

    if queryset is None:
        queryset = Person.objects.all()

    invalid = get_invalid_group_members(group, queryset)
    invalid_pks = [p.pk for p in invalid]
    queryset = queryset\
        .annotate(num_groups=Count('groups', distinct=True))\
        .filter(groups=group)\
        .exclude(pk__in=invalid_pks)

    return queryset


def get_start_end_for_competition():

    return None, None  # Competition done.

    start = parse_datetime("2018-10-15 12:00:00")
    start = pytz.timezone("Pacific/Auckland").localize(start, is_dst=None)
    end = parse_datetime("2018-10-22 12:00:00")
    end = pytz.timezone("Pacific/Auckland").localize(end, is_dst=None)

    return start, end


def filter_qs_for_competition(queryset):
    '''Takes a recording or QC queryset and returns only recordings to be used
    during the competition.'''
    start, end = get_start_end_for_competition()

    if start is None:
        return queryset

    # Only do this when comp hasn't started. If comp ended, still show just the
    # comp data.
    if timezone.now() < start:
        return queryset

    queryset = queryset\
        .filter(updated__lte=end)\
        .filter(updated__gte=start)

    return queryset


def get_competition_group_score(group):
    # ERROR! This doesn't consder language!
    members = get_valid_group_members(group)
    if members is None:
        return 0

    SCORE_KEY = "COMP-GROUP-SCORE-{0}".format(group.pk)
    COUNT_KEY = "COMP-GROUP-COUNT-{0}".format(group.pk)
    score = cache.get(SCORE_KEY)
    count = cache.get(COUNT_KEY)
    if score is None:
        score = 0
        count = 0
        for person in members:
            p_score, p_count = get_competition_person_score(group, person)
            score = score + p_score
            count = count + p_count
        score = int(score)
        cache.set(SCORE_KEY, score, 60*10)
        cache.set(COUNT_KEY, count, 60*10)
    return score, count


def get_competition_person_score(group, person):
    # start, end = get_start_end_for_competition()
    start = parse_datetime("2018-03-15 13:00:00")
    start = pytz.timezone("Pacific/Auckland").localize(start, is_dst=None)
    end = parse_datetime("2018-03-25 18:00:00")
    end = pytz.timezone("Pacific/Auckland").localize(end, is_dst=None)

    # ERROR! This doesn't consdier language!
    members = get_valid_group_members(group)
    if members is None:
        return 0

    # IMPORTANT CHANGE - LET THEM NO THEIR SCORES WILL SHOW HERE SO THAT
    # WHEN THEIR USER BECOMES VALID THEY'LL GET THEIR SCORES
    # if not members.filter(pk=person.pk).exists():
    #     return 0

    recordings = Recording.objects\
        .filter(Q(person=person) &
                Q(created__lte=end) &
                Q(created__gte=start))

    reviews = RecordingQualityControl.objects\
        .filter(Q(person=person) &
                Q(updated__gte=end) &
                Q(updated__lte=start))

    SCORE_KEY = "COMP-PERSON-SCORE-{0}".format(person.pk)
    score = cache.get(SCORE_KEY)
    if score is None:
        score = 0
        for r in recordings:
            score = score + r.calculate_score()
        for q in reviews:
            score = score + q.calculate_score()
        cache.set(SCORE_KEY, score, 60*5)
    return score, recordings.count()


# TODO TEST THIS!
# Why did we make this?
# def calculate_recording_score(recording):
#     """Score awarded for uploading this recording. """
#     # start, end = get_start_end_for_competition()
#     start = parse_datetime("2018-03-18 13:00:00")
#     start = pytz.timezone("Pacific/Auckland").localize(start, is_dst=None)
#     end = parse_datetime("2018-03-19 13:00:00")
#     end = pytz.timezone("Pacific/Auckland").localize(end, is_dst=None)

#     factor_1 = 1
#     if recording.created > start and recording.created < end:
#         factor_1 = 2

#     approved = recording.quality_control \
#         .filter(person__user__is_staff=True) \
#         .filter(approved=True)

#     if approved.count() >= 1:
#         return 1

#     net_votes = recording.quality_control \
#         .filter(person__user__is_staff=True) \
#         .aggregate(value=Sum(F('good') - F('bad')))

#     net_votes = decimal.Decimal(net_votes['value'] or 0)

#     if net_votes != 0:
#         net_votes = net_votes/abs(net_votes)

#     damper = 4
#     score = max(0, 1 - math.exp(-(net_votes + 1) / damper))

#     if net_votes == 0:
#         return score * factor_1
#     else:
#         return score


'''
=============================================================================
Below are methods to help with reviewing faster and doing other custom stuffs
=============================================================================
'''


def mahi_tahi(group):
    '''Returns the growth rate for a group during a period of time'''
    start = parse_datetime("2018-03-22 13:00:00")
    start = pytz.timezone("Pacific/Auckland").localize(start, is_dst=None)
    end = parse_datetime("2018-03-23 13:00:00")
    end = pytz.timezone("Pacific/Auckland").localize(end, is_dst=None)

    members = get_valid_group_members(group)

    num_recordings = 0.0
    num_members = 0.0
    for person in members:
        recordings = Recording.objects\
            .filter(person=person)\
            .filter(created__lte=end)\
            .filter(created__gte=start)
    # if recordings.count() != 0:
        num_recordings = num_recordings + recordings.count()
        num_members = num_members + 1.0

    if num_members == 0:
        return 0

    return num_recordings/num_members


def filter_recordings_to_top_ten(queryset):

    # Only consider groups with large amount of recordings
    # new_queryset = queryset.filter(person__groups__num_recordings__gte=5000)

    # if new_queryset.count() == 0:
    #     return queryset
    # else:
    #     queryset = queryset.filter(person__groups__num_recordings__gte=5000)

    # Find groups with low review rate AND more than 5000 recordings
    groups = Group.objects.all() \
        .annotate(
            review_rate=Cast(Count(
                'person__recording__quality_control', distinct=True
                ), FloatField())/Cast(
                1+F('num_recordings'), FloatField())
        ) \
        .filter(num_recordings__gte=7000)

    avg_rate = groups.aggregate(Avg('review_rate'))
    if avg_rate['review_rate__avg'] is not None:
        groups = groups \
            .filter(review_rate__lte=avg_rate['review_rate__avg'])

    logger.debug(u'Average Review Rate: {0}'.format(
        avg_rate['review_rate__avg']))
    logger.debug(u'These groups are being reviewed:{0}'.format(
        [u'{0}:{1}:{2:0.1f}'.format(
            g.pk, g.name, g.review_rate*100) for g in groups]))

    count = groups.count()
    if count > 1:
        i = random.randint(0, groups.count() - 1)
        group = groups[i]
    else:
        return queryset

    valid_members = get_valid_group_members(group)
    queryset = queryset.filter(person__in=valid_members)

    return queryset

    # queryset = queryset \
    #     .annotate(
    #         review_rate=Cast(Count(
    #             'person__recording__quality_control'
    #         ), FloatField())/Cast(
    #             Count('person__recording'), FloatField())
    #         )\


    # avg_rate = queryset.aggregate(Avg('review_rate'))

    # # Filter out so that we review people who haven't had equal reviewing
    # # opportunity.

    # if avg_rate['review_rate__avg'] is not None:

    #     queryset = queryset \
    #         .filter(review_rate__lte=avg_rate['review_rate__avg'])

    # return queryset


def filter_recordings_distribute_reviews(queryset):

    # Find people with low review rates
    people = Person.objects.all() \
        .annotate(
            num_recordings=Count('recording'))\
        .filter(
            num_recordings__gte=1)\
        .annotate(
            review_rate=Cast(Count(
                'recording__quality_control', distinct=True
                ), FloatField())/Cast(
                1+F('num_recordings'), FloatField())
        )

    avg_rate = people.aggregate(Avg('review_rate'))
    if avg_rate['review_rate__avg'] is not None:
        people = people \
            .filter(review_rate__lte=avg_rate['review_rate__avg'])

    logger.debug(u'Average People Review Rate: {0}'.format(
        avg_rate['review_rate__avg']))

    logger.debug(u'Average People Review Rate: {0}'.format(
        avg_rate['review_rate__avg']))

    count = people.count()
    if count > 1:

        i = random.randint(0, people.count() - 1)
        person = people[i]
        queryset = queryset.filter(person=person)

    return queryset
