# -*- coding: utf-8 -*-

from django.conf.urls import url, include
# from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

from corpora.views import views
from corpora.views.vue import VueFrontend
from corpora.views.management import UserCheckView
from django.views.generic import RedirectView
# from people.views import profile_redirect
from rest_framework.documentation import include_docs_urls

from corpus.views.stats_views import RecordingStatsView
from corpus.views.views import StatsView
from people.views import stats_views, auth
from people.views import views as people_views
from message.views import RenderEmailView
from django.views.decorators.cache import cache_page

from django.conf import settings
from django.conf.urls import include, url
from django.urls import path, re_path

urlpatterns = [

    url(r'^magic', people_views.MagicLogin.as_view(), name="magic"),

    url(r'^$',
        views.HomeView.as_view(),
        name='home'),

    url(r'^privacy',
        cache_page(60 * 15)(
            views.privacy),
        name='privacy'),

    url(r'^', include(('corpus.urls', 'corpus'), namespace='corpus')),
    url(r'^', include(('transcription.urls', 'transcription'), namespace='transcription')),


    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('allauth.urls')),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^signup/',
        RedirectView.as_view(
            permanent=False,
            query_string=True,
            url='/accounts/signup'),
        name='signup'),

    url(r'^login/',
        RedirectView.as_view(
            permanent=False,
            query_string=True,
            url='/accounts/login'),
        name='login'),

    url(_(r'^people/'), include(('people.urls','people'), namespace='people')),
    # url(r'^people/profile', profile_redirect, name='profile-backwards-comp'),

    url(r'^rules/$',
        RedirectView.as_view(
            permanent=True,
            url='/competition/rules'),
        name='rules-redirect'),

    url(_(r'^competition/rules'),
        views.rules,
        name='rules'),

    url(_(r'^competition/help'),
        people_views.Help.as_view(),
        name='competition_help'),

    url(_(r'^competition/user_leaderboard'),
        stats_views.PeopleRecordingStatsView.as_view(),
        name='user_leaderboard'),

    url(_(r'^competition/group/(?P<pk>\d+)'),
        stats_views.GroupStatsView.as_view(),
        name='competition_group'),

    url(_(r'^competition/top20$'),
        stats_views.Top20.as_view(),
        name='competition_top20'),

    url(_(r'^competition/mahitahi$'),
        stats_views.MahiTahi.as_view(),
        name='competition_mahitahi'),

    url(_(r'^competition'),
        people_views.Competition.as_view(),
        name='competition'),

    url(_(r'^stats/person_qc'),
        stats_views.PersonQCStatsView.as_view(),
        name='stats_person_qc'),

    url(_(r'^stats/person'),
        stats_views.PersonRecordingStatsView.as_view(),
        name='stats_person'),

    url(_(r'^stats/people$'),
        stats_views.PeopleRecordingStatsView.as_view(),
        name='stats_people'),

    url(_(r'^stats/reviewers'),
        stats_views.PeopleQCStatsView.as_view(),
        name='stats_reviewers'),

    url(_(r'^stats/groups$'),
        stats_views.GroupsStatsView.as_view(),
        name='stats_groups'),

    url(_(r'^stats/recordings'),
        RecordingStatsView.as_view(),
        name='stats_recordings'),

    url(_(r'^stats/$'),
        StatsView.as_view(),
        name='stats'),


    url(r'^', include(('corpora.urls_api','api'), namespace='api')),
    url(r'^docs/', include_docs_urls(title='Corpora API', public=False)),

    url(
        r'^expo-login/(?P<redirect_url>.*)',
        auth.ProcessExpoRedirect.as_view(),
        name='expo-login'),

    re_path(r'^v/$.*', VueFrontend.as_view()),
    re_path(r'^v/.*/$', VueFrontend.as_view()),

    path('management', UserCheckView.as_view()),
    # url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
    #     name='django.contrib.sitemaps.views.sitemap')

    path('health-check', views.health_check),
    path('render-email', RenderEmailView.as_view()),
    path('message/', include(('message.urls', 'message'), namespace='message')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


# I think it's better we store language preference in cookie and not do url redirects
# urlpatterns += i18n_patterns(
#     url( _(r'^people/'), include('people.urls', namespace='people')),
# )
# prefix_default_language=True