# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

from django.views.generic.list import ListView
from django.views.generic.base import TemplateView

from corpus.models import Recording, RecordingQualityControl
from people.helpers import get_current_language

import datetime
from django.utils import timezone

from django.db.models import Sum

from corpora.mixins import SiteInfoMixin
from people.views.stats_views import JSONResponseMixin

import logging
logger = logging.getLogger('corpora')


class RecordingStatsView(JSONResponseMixin, SiteInfoMixin, TemplateView):
    template_name = 'corpus/recordings_stats_list.html'
    # paginate_by = 50
    context_object_name = 'recordings'
    x_title = _('Recording Growth Rate.')
    x_description = _('Graph of recording growth over the last month.')

    def render_to_response(self, context):
        context['view'] = None
        context['person'] = None
        if self.request.GET.get('format') == 'json':
            return self.render_to_json_response(context)
        else:
            return super(RecordingStatsView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(RecordingStatsView, self).get_context_data(**kwargs)
        user = self.request.user

        language = get_current_language(self.request)

        recordings = Recording.objects.all().order_by('-created')
        reviews = RecordingQualityControl.objects\
            .all()\
            .order_by('-updated')

        start_date = self.request.GET.get('start_date', None)
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        except:
            start_date = timezone.now() - datetime.timedelta(days=30)

        end_date = self.request.GET.get('end_date', None)
        try:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except:
            end_date = timezone.now()

        start_day = \
            timezone.make_aware(
                datetime.datetime.combine(start_date, datetime.time()),
                timezone.get_default_timezone())

        end_day = \
            timezone.make_aware(
                datetime.datetime.combine(end_date, datetime.time()),
                timezone.get_default_timezone())

        day_counter = 1
        timezone_shift = datetime.timedelta(hours=0)
        day_offset = datetime.timedelta(days=day_counter)
        next_day = start_day - day_offset
        data = {
            'recordings': {},
            'growth_rate': {},
            'reviews': {},
            'reviews_growth': {}
        }

        data = {
            'recordings': {
                'labels': [],
                'values': [],
            },
            'growth_rate': {
                'labels': [],
                'values': [],
            },
            'reviews': {
                'labels': [],
                'values': [],
            },
            'reviews_growth': {
                'labels': [],
                'values': [],
            },
        }

        r = recordings.filter(
            created__lt=start_day+timezone_shift)\
            .aggregate(Sum('duration'))

        if r['duration__sum']:
            total_recordings = r['duration__sum']/60
        else:
            total_recordings = 0
        total_reviews = 0
        counter = 0
        tomorrow = next_day + day_offset
        # next_day = next_day
        while next_day < end_day - timezone_shift:

            if counter == 0:
                start_30days_back = start_day
                # if start_30days_back > next_day:
                tomorrow = timezone.make_aware(
                        datetime.datetime.combine(start_30days_back, datetime.time()),
                        timezone.get_default_timezone())
            r = recordings.filter(
                created__gte=next_day+timezone_shift,
                created__lt=tomorrow+timezone_shift)\
                .aggregate(Sum('duration'))
            if r['duration__sum'] is None:
                r['duration__sum'] = 0

            total_recordings = (r['duration__sum']/60) + total_recordings

            data['recordings']['labels'].append(
                (next_day).strftime('%d-%m-%y'))
            data['recordings']['values'].append(total_recordings)

            try:
                data['growth_rate']['labels'].append(
                    (next_day).strftime('%d-%m-%y'))
                data['growth_rate']['values'].append(
                    total_recordings - data['recordings']['values'][counter-1])
            except IndexError:
                data['growth_rate']['values'].append(total_recordings)

            qc = reviews.filter(
                updated__gte=next_day+timezone_shift,
                updated__lt=tomorrow+timezone_shift)
            num_reviews = qc.count()
            total_reviews = total_reviews + num_reviews

            data['reviews']['labels'].append(
                (next_day).strftime('%d-%m-%y'))
            data['reviews']['values'].append(total_reviews)

            try:
                data['reviews_growth']['labels'].append(
                    (next_day).strftime('%d-%m-%y'))
                data['reviews_growth']['values'].append(
                    total_reviews - data['reviews']['values'][counter-1])
            except IndexError:
                data['reviews_growth']['values'].append(total_reviews)


            # try:
            #     next_day = timezone.make_aware(
            #         tomorrow,
            #         timezone.get_default_timezone())
            # except:
            next_day = tomorrow
            tomorrow = tomorrow + day_offset
            counter = counter + 1

        # context['labels'] = [key for key in data['recordings']]
        # context['values'] = [
        #     "{0:0.2d}".format(data['recordings'][i]) for i in data['recordings']]

        context['data'] = data
        context['start_day'] = start_day
        context['end_day'] = end_day
        context['start_date'] = start_date
        context['end_date'] = end_date

        return context
