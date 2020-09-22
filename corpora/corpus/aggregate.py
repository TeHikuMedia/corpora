# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.utils.translation import ugettext as _
from corpus.models import Recording, Sentence, \
    SentenceQualityControl, \
    RecordingQualityControl
from django.db.models import Sum, Count, When, Value, Case, IntegerField
from django.db.models import Q, F


def get_num_approved(query):
    d = query\
        .aggregate(sum_approved=Sum(
            Case(
                When(
                    quality_control__isnull=True,
                    then=Value(0)),
                When(
                    quality_control__approved=True,
                    then=Value(1)),
                When(
                    quality_control__approved=False,
                    then=Value(0)),
                default=Value(0),
                output_field=IntegerField())))
    return d['sum_approved']


def get_net_votes(query):

    net_votes = query \
        .filter(quality_control__person__user__is_staff=True) \
        .annotate(net_vote=Sum(
            F('quality_control__good') - F('quality_control__bad')))

    goods = net_votes.filter(net_vote__gte=1)
    bads = net_votes.filter(net_vote__lte=-1)

    return (goods.count(), bads.count())

    # d1 = query\
    #     .aggregate(total_up_votes=Sum('quality_control__good'))
    # d2 = query\
    #     .aggregate(total_down_votes=Sum('quality_control__bad'))

    # return (d1['total_up_votes'], d2['total_down_votes'])


def build_recordings_stat_dict(recording_queryset):
    duration = recording_queryset.aggregate(Sum('duration'))
    approved_recordings = \
        recording_queryset.filter(quality_control__approved=True)
    recording_votes = get_net_votes(recording_queryset)

    reviewed_recordings = recording_queryset\
        .exclude(quality_control__isnull=True)

    if duration['duration__sum'] is None:
        total_seconds = 0
    else:
        total_seconds = float(duration['duration__sum'])
    hours = int(total_seconds/(60.0*60))
    minutes = int((total_seconds - (60*60.0)*hours)/60.0)
    seconds = int(total_seconds - (60*60.0)*hours - 60.0*minutes)

    num_reviewed = reviewed_recordings.count()
    num_approved = approved_recordings.count()
    stats = {
        'total': recording_queryset.count(),
        'num_approved': num_approved,
        'up_votes': recording_votes[0],
        'down_votes': recording_votes[1],
        'reviews': {
            'num_reviewed': num_reviewed,
        },
        'duration_display': "{:02d}:{:02d}:{:02d} ".format(
            hours, minutes, seconds),
        'total_seconds': int(total_seconds),
        'total_minutes': int(total_seconds/60.0),
        'dimension_string': _('seconds') if total_seconds < 60 else _('minutes'),
        'duration_string': int(total_seconds) if total_seconds < 60 else int(total_seconds/60.0)
    }

    if num_reviewed > 0:
        stats['reviews'] = {
            'num_reviewed': num_reviewed,
            'approval_rate': 100.0*num_approved/num_reviewed,
            'up_rate': 100.0*recording_votes[0]/num_reviewed,
            'down_rate': 100.0*recording_votes[1]/num_reviewed
            }

    if stats['up_votes'] is None:
        stats['up_votes'] = 0

    if stats['down_votes'] is None:
        stats['down_votes'] = 0

    if stats['num_approved'] is None:
        stats['num_approved'] = 0

    return stats


# This assumes recording QCs
def build_qualitycontrol_stat_dict(queryset):

    approved = \
        queryset.filter(approved=True)

    goods = queryset.filter(good__gte=1).aggregate(sum=Sum('good'))
    bads = queryset.filter(bad__gte=1).aggregate(sum=Sum('bad'))
    deletes = queryset.filter(trash=True)
    stars = queryset.filter(star__gte=1).aggregate(sum=Sum('star'))

    stats = {
        'count': queryset.count(),
        'approved': approved.count(),
        'good': goods['sum'] if goods['sum'] is not None else 0,
        'bad': bads['sum'] if bads['sum'] is not None else 0,
        'trash': deletes.count(),
        'delete': deletes.count(),
        'star': stars['sum'] if stars['sum'] is not None else 0,
    }

    return stats
