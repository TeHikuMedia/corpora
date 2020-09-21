# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.template.context import RequestContext
from django.forms import modelform_factory
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden

from django.urls import reverse, resolve
from django.utils import timezone
import datetime
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned, PermissionDenied
import json
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView, MultipleObjectMixin
from django.views.generic.detail import DetailView
from django.middleware.csrf import CsrfViewMiddleware

from django.contrib.contenttypes.models import ContentType

from corpus.models import Recording, Sentence, \
    RecordingQualityControl, \
    SentenceQualityControl
from people.models import Person, KnownLanguage, Group
from people.tasks import send_person_emails
from people.forms import SendEmailForm
from corpus.helpers import get_next_sentence
from people.helpers import \
    get_or_create_person,\
    get_person,\
    get_current_language,\
    email_verified,\
    get_email_object

from django.conf import settings

from allauth.account.models import EmailAddress

from django import http
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from boto.s3.connection import S3Connection

from django.db.models import Sum, Count, When, Value, Case, IntegerField, Q, FloatField, F, CharField
from django.db.models.functions import Cast

from django.core.cache import cache

from corpus.aggregate import \
    build_recordings_stat_dict, build_qualitycontrol_stat_dict

from django.contrib.auth.mixins import UserPassesTestMixin

from django.db import models

from corpora.mixins import SiteInfoMixin, EnsureCsrfCookieMixin

from people.competition import \
    get_competition_group_score,\
    get_valid_group_members,\
    get_invalid_group_members,\
    get_competition_person_score, \
    filter_qs_for_competition, \
    mahi_tahi, \
    get_start_end_for_competition

from people.forms import \
    ResendEmailVerificationForm

import logging
logger = logging.getLogger('corpora')


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        return context


class PersonRecordingStatsView(JSONResponseMixin, TemplateView):
    template_name = 'people/stats/person_recording_stats_view_detail.html'

    def get_context_data(self, **kwargs):
        context = \
            super(PersonRecordingStatsView, self).get_context_data(**kwargs)

        person = get_person(self.request)
        language = get_current_language(self.request)

        recordings = Recording.objects.filter(
            sentence__language=language,
            person=person)

        # Assume for now user is in NZ timezone = UTC + 12 hours
        time_offset = 0
        now = timezone.now() + datetime.timedelta(hours=time_offset)

        # Find the day for NZ, then take us back to utc time.
        today_begining = \
            datetime.datetime.combine(now, datetime.time()) - \
            datetime.timedelta(hours=time_offset)

        # This logical is compared against utc time - the default timezone for our data
        # I presume django deals with this timezoen stuff anyway?
        todays_recordings = recordings.filter(created__gte=today_begining).order_by('created')

        stats = {
            'recordings': build_recordings_stat_dict(recordings),
            'recordings_today': build_recordings_stat_dict(todays_recordings)
        }

        stats['recordings_today']['start_time'] = today_begining
        stats['recordings_today']['end_time'] = timezone.now()
        if todays_recordings:
            stats['recordings_today']['earliest_time'] = todays_recordings[0].created
            stats['recordings_today']['latest_time'] = todays_recordings[todays_recordings.count()-1].created

        context['person'] = person
        context['stats'] = stats

        return context

    def render_to_response(self, context):
        if self.request.GET.get('format') == 'json':
            return self.render_to_json_response(context)
        else:
            return super(PersonRecordingStatsView, self).render_to_response(context)

    def get_data(self, context):
        return context['stats']


# This is currently only for recording QCs
class PersonQCStatsView(JSONResponseMixin, TemplateView):
    template_name = 'people/stats/person_qc_stats_view_detail.html'

    def get_context_data(self, **kwargs):
        context = \
            super(PersonQCStatsView, self).get_context_data(**kwargs)

        person = get_person(self.request)
        language = get_current_language(self.request)

        qcs = RecordingQualityControl.objects\
            .filter(person=person)\
            .filter(recording__language=language)

        now = timezone.now()

        today_begining = \
            datetime.datetime.combine(now, datetime.time())

        todays_qcs = qcs\
            .filter(updated__gte=today_begining).order_by('updated')

        stats = {
            'qcs': build_qualitycontrol_stat_dict(qcs),
            'qcs_today': build_qualitycontrol_stat_dict(todays_qcs)
        }

        context['person'] = person
        context['stats'] = stats

        return context

    def render_to_response(self, context):
        if self.request.GET.get('format') == 'json':
            return self.render_to_json_response(context)
        else:
            return super(PersonQCStatsView, self).render_to_response(context)

    def get_data(self, context):
        return context['stats']


class PeopleRecordingStatsView(SiteInfoMixin, UserPassesTestMixin, ListView):
    model = Person
    template_name = 'people/stats/leaderboard.html'
    paginate_by = 50
    context_object_name = 'people'
    x_title = _('Leaderboard')
    x_description = \
        _("Leaderboard for people who've contributed to our corpus.")

    def test_func(self):
        return True
        # return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = \
            super(PeopleRecordingStatsView, self).get_context_data(**kwargs)
        start, end = get_start_end_for_competition()
        if start is not None:
            context['competition'] = True
        else:
            context['competition'] = False
        return context

    def get_queryset(self):
        # language = get_current_language(self.request)
        people = Person.objects.all()
        start, end = get_start_end_for_competition()
        if start is not None:
            return people.order_by('-num_recordings_com')
        else:
            return people.order_by('-num_recordings')

        # start, end = get_start_end_for_competition()
        # if start is not None:
        #     people = Person.objects.all()\
        #         .annotate(
        #             num_reviewed=models.Count(
        #                 Case(
        #                     When(Q(recordingqualitycontrol__updated__gte=start) &
        #                          Q(recordingqualitycontrol__updated__lte=end),
        #                          then=F('recordingqualitycontrol')),
        #                     output_field=CharField()), distinct=True))\
        #         .annotate(
        #             num_recordings=models.Count(
        #                 Case(
        #                     When(Q(recording__created__gte=start) &
        #                          Q(recording__created__lte=end),
        #                          then=F('recording')),
        #                     output_field=CharField()), distinct=True))\
        #         .order_by('-num_recordings')

        # else:
        #     people = Person.objects.all()\
        #         .annotate(
        #             num_reviewed=models.Count(
        #                 'recordingqualitycontrol', distinct=True))\
        #         .annotate(
        #             num_recordings=models.Count(
        #                 'recording', distinct=True))\
        #         .order_by('-num_recordings')

        # return people


# This is currently only for recording QCs
class PeopleQCStatsView(UserPassesTestMixin, ListView):
    model = Person
    template_name = 'people/stats/person_qc_stats_view_list.html'
    paginate_by = 50
    context_object_name = 'people'
    x_title = _('Reviewer Stats')
    x_description = \
        _("Leaderboard for reviewers.")

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):

        person = get_person(self.request)
        language = get_current_language(self.request)

        people = Person.objects.filter(user__is_staff=True)

        people = people\
            .annotate(
                num_approved=models.Sum(
                    Case(
                        When(
                            recordingqualitycontrol__isnull=True,
                            then=Value(0)),
                        When(
                            recordingqualitycontrol__approved=True,
                            then=Value(1)),
                        When(
                            recordingqualitycontrol__approved=False,
                            then=Value(0)),
                        default=Value(0),
                        output_field=IntegerField())))\
            .annotate(
                num_good=models.Sum(
                    Case(
                        When(
                            recordingqualitycontrol__isnull=True,
                            then=Value(0)),
                        When(
                            recordingqualitycontrol__good__gte=1,
                            then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField())))\
            .annotate(
                num_bad=models.Sum(
                    Case(
                        When(
                            recordingqualitycontrol__isnull=True,
                            then=Value(0)),
                        When(
                            recordingqualitycontrol__bad__gte=1,
                            then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField())))\
            .order_by('-num_reviews')

        return people


class GroupsStatsView(SiteInfoMixin, UserPassesTestMixin, ListView):
    model = Group
    template_name = 'people/stats/groups_leaderboard.html'
    paginate_by = 50
    context_object_name = 'groups'
    x_title = _('Group Leaderboard')
    x_description = _("Group leaderboard of all the groups contributing corpus\
to our project.")

    def test_func(self):
        return self.request.user.is_staff and self.request.user.is_authenticated

    def get_queryset(self):
        # language = get_current_language(self.request)
        groups = Group.objects.all().order_by('-score')\
            .annotate(
                review_rate=Cast(Count(
                    'person__recording__quality_control', distinct=True
                    ), FloatField())/Cast(
                    1+Count(
                        'person__recording', distinct=True
                    )*1.0, FloatField())
                ) \
            .annotate(
                approval_rate=Sum(
                    Case(
                        When(
                            person__recording__quality_control__isnull=True,
                            then=Value(0)),
                        When(
                            person__recording__quality_control__approved=True,
                            then=Value(1)),
                        When(
                            person__recording__quality_control__approved=False,
                            then=Value(0)),
                        default=Value(0),
                        output_field=FloatField())) /
                Cast(1+Count(
                    'person__recording__quality_control', distinct=True
                    ), FloatField()
                )
            ) \
            .annotate(size=Count('person', distinct=True))

        sort_by = self.request.GET.get('sort_by', '')
        if '-score' in sort_by:
            groups = groups.order_by('-score')
        elif 'score' in sort_by:
            groups = groups.order_by('score')
        elif '-members' in sort_by:
            groups = groups.order_by('-size')
        elif 'members' in sort_by:
            groups = groups.order_by('size')
        elif '-num_recordings' in sort_by:
            groups = groups.order_by('-num_recordings')
        elif 'num_recordings' in sort_by:
            groups = groups.order_by('num_recordings')
        elif '-review_rate' in sort_by:
            groups = groups.order_by('-review_rate')
        elif 'review_rate' in sort_by:
            groups = groups.order_by('review_rate')
        elif '-approval_rate' in sort_by:
            groups = groups.order_by('-approval_rate')
        elif 'approval_rate' in sort_by:
            groups = groups.order_by('approval_rate')
        elif '-duration' in sort_by:
            groups = groups.order_by('-duration')
        elif 'duration' in sort_by:
            groups = groups.order_by('duration')
        else:
            groups = groups.order_by('-score')

        return groups

    def get_context_data(self, **kwargs):
        context = \
            super(GroupsStatsView, self).get_context_data(**kwargs)

        language = get_current_language(self.request)

        groups = context['groups']

        # for group in groups:
        #     # members = get_valid_group_members(group)
        #     # recordings = filter_qs_for_competition(
        #     #     Recording.objects.filter(person__in=members))
        #     group.duration_hours = group.duration/60/60

        # Tryin to do sort stuff :/
        path = self.request.get_full_path()
        if '?' not in path:
            path = path+'?sort_by=-score&page=1'

        context['path'] = path

        # context['groups'] = groups
        return context


class Top20(GroupsStatsView):
    model = Group
    template_name = 'people/stats/top_20.html'
    paginate_by = 20
    context_object_name = 'groups'
    x_title = _('Top 20 Groups ')
    x_description = _("Groups in the Top 20 of the competition.")

    def test_func(self):
        return self.request.user.is_staff and \
            self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = \
            super(Top20, self).get_context_data(**kwargs)

        recordings = Recording.objects.all()
        recordings = filter_qs_for_competition(recordings)
        total_recordings = recordings.count()

        total_duration = recordings.aggregate(total_duration=Sum('duration'))
        total_duration = total_duration['total_duration']

        if total_duration is not None:
            total_duration = total_duration/3600
        else:
            total_duration = 0

        groups = Group.objects.all()

        num_people = groups \
            .aggregate(num_people=Count('person', distinct=True))
        num_people = num_people['num_people']
        if num_people is None:
            num_people = 0
        num_groups = groups.count()

        context['num_people'] = num_people
        context['num_groups'] = num_groups
        context['total_duration'] = total_duration
        context['total_recordings'] = total_recordings

        return context

    # def get_queryset(self):
    #     queryset = super(Top20, self).get_queryset()


class MahiTahi(GroupsStatsView):
    model = Group
    template_name = 'people/stats/mahitahi.html'
    paginate_by = 100
    context_object_name = 'groups'
    x_title = _('Mahi Tahi Growth Rate')
    x_description = _("Mahi Tahi.")

    def test_func(self):
        return self.request.user.is_staff and \
            self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = \
            super(MahiTahi, self).get_context_data(**kwargs)

        language = get_current_language(self.request)

        groups = context['groups']

        for group in groups:
            group.growth_rate = mahi_tahi(group)

        context['groups'] = groups
        return context


class GroupStatsView(
        EnsureCsrfCookieMixin, SiteInfoMixin, UserPassesTestMixin, DetailView):
    model = Group
    template_name = 'people/stats/group_leaderboard.html'
    context_object_name = 'group'
    x_title = _('Individual Group Leaderboard')
    x_description = _("Leaderboard for people of a particular group.")

    def test_func(self):
        person = get_person(self.request)
        path = self.request.get_full_path()
        pk = int(path.split('/')[-1])

        if self.request.user.is_staff:
            return True
        elif person is None:
            return False
        elif person.groups.filter(pk__in=[pk]).exists():
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = \
            super(GroupStatsView, self).get_context_data(**kwargs)

        group = context['group']

        context['x_title'] = _('Group Leaderboard: {0}').format(group)
        context['x_description'] = _("Leaderboard for members of {0}.").format(
            group)

        language = get_current_language(self.request)

        people = Person.objects.all()

        valid_members = people
        valid_members = get_valid_group_members(group, valid_members)

        invalid_members = people
        invalid_members = get_invalid_group_members(group, invalid_members)

        # people = people\
        #     .filter(recording__sentence__language=language)

        # score, count = get_competition_group_score(group)
        num_recordings = 0
        if valid_members:
            for member in valid_members:
                recordings = filter_qs_for_competition(
                    Recording.objects.filter(person=member))
                member.num_recordings = recordings.count()

        if invalid_members:
            invalid_members = invalid_members\
                .annotate(num_groups=Count('groups', distinct=True))

            for member in invalid_members:
                recordings = filter_qs_for_competition(
                    Recording.objects.filter(person=member))
                member.num_recordings = recordings.count()
                member.verified = email_verified(member)

        form = ResendEmailVerificationForm()

        group.duration_hours = group.duration/60/60

        context['group'] = group
        context['score'] = group.score
        context['form'] = form
        context['people'] = people.filter(groups=group)
        context['valid_members'] = valid_members
        context['invalid_members'] = invalid_members

        return context

    def post(self, request, *args, **kwargs):
        reason = CsrfViewMiddleware().process_view(request, None, (), {})
        if reason:
            raise PermissionDenied

        person = get_or_create_person(request)

        form = ResendEmailVerificationForm(request.POST)
        if form.is_valid():
            email_object, created = get_email_object(person)
            email_object.send_confirmation()

        return super(GroupStatsView, self).get(request, *args, **kwargs)


class PeopleEmailsView(UserPassesTestMixin, ListView):
    model = Person
    template_name = 'people/people_email_list.html'
    context_object_name = 'people'
    raise_exception = True
    paginate_by = 495

    def test_func(self):
        return self.request.user.is_superuser \
            and self.request.user.is_authenticated

    def get_queryset(self):
        return Person.objects\
            .filter(Q(profile_email__isnull=False) | Q(user__isnull=False))\
            .exclude(receive_weekly_updates=False)\
            .order_by('full_name')

    def get_context_data(self, **kwargs):
        context = \
            super(PeopleEmailsView, self).get_context_data(**kwargs)

        form = SendEmailForm()
        context['form'] = form

        people = context['people']

        for person in context['people']:
            if person.user is not None:
                try:
                    email = EmailAddress.objects.get(user=person.user)
                    email = email.email
                except ObjectDoesNotExist:
                    email = person.user.email
                except MultipleObjectsReturned:
                    try:
                        email = EmailAddress.objects.get(
                            user=person.user, verified=True)
                        email = email.email
                    except ObjectDoesNotExist:
                        email = EmailAddress.objects.filter(user=person.user).first()
                        email = email.email
            else:
                email = person.profile_email

            person.email = email

        return context

    def post(self, request, *args, **kwargs):
        reason = CsrfViewMiddleware().process_view(request, None, (), {})
        if reason:
            raise PermissionDenied

        if not self.request.user.is_superuser and \
                self.request.user.is_authenticated:
            return HttpResponseForbidden()

        # Everything is okay - so let's send emails?

        form = SendEmailForm(request.POST)
        if form.is_valid():
            freq = []
            if form.cleaned_data['weekly']:
                freq.append(_('weekly'))
            if form.cleaned_data['daily']:
                freq.append(_('daily'))

            for f in freq:
                send_person_emails.apply_async(
                    countdown=2,
                    task_id='send_{0}_emails-{1}'.format(
                        f, timezone.now().strftime("%y%m%d-%H")),
                    args=[f])

        return super(PeopleEmailsView, self).get(request, *args, **kwargs)
