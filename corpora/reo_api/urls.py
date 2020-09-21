# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url, include
# from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

from reo_api.views import (
    HomeView, DocsDashboardView, BrowseAPIDashboardView, TokenView)

from django.views.generic import RedirectView


from people.views import views as people_views

from django.views.decorators.cache import cache_page
from rest_framework.documentation import include_docs_urls
from transcription.views import api as transcription_api
from rest_framework import routers
from rest_framework.authtoken import views


urlpatterns = [

    url(r'^$',
        HomeView.as_view(),
        name='home'),

    # url(r'^dash/docs$',
    #     CustomDocsView.as_view(),
    #     name='dashboard-docs'),

    # url(r'^dash/api$',
    #     BrowseAPIDashboardView.as_view(),
    #     name='dashboard-api'),

    # url(r'^privacy',
    #     cache_page(60 * 15)(
    #         views.privacy),
    #     name='privacy'),

    url(r'^', include(('transcription.urls', 'reo_api'), namespace='transcription')),

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

    # url(_(r'^people/'), include('people.urls', namespace='people')),

]


router = routers.DefaultRouter()
# router.register(r'groups', corpora_api.GroupViewSet)
# router.register(r'users', corpora_api.UserViewSet)

# router.register(r'tribes', people_api.TribeViewSet)
# router.register(r'demographics', people_api.DemographicViewSet)
# router.register(r'persons', people_api.PersonViewSet)
# router.register(r'knownlangauges', people_api.KnownLanguageViewSet)
# router.register(r'accept_license', license_api.AcceptLicenseViewSet)

# router.register(r'transcriptions', transcription_api.TranscriptionViewSet)

router.register(
    r'transcription-segment', transcription_api.TranscriptionSegmentViewSet)
router.register(
    r'transcription', transcription_api.AudioFileTranscriptionViewSet)

docs_patterns = router.urls

urlpatterns += [

    # url(r'^api/sentences/$', corpus_api.SentencesView.as_view()),
    url(r'^api/token', TokenView.as_view()),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include(
        'rest_framework.urls',
        namespace='rest_framework')),

]

urlpatterns += [
    url(r'^api-token-auth/', views.obtain_auth_token),
]


urlpatterns += [
    url(r'^docs/', include_docs_urls(
        title='koreromaori.io',
        public=True,
        patterns=docs_patterns,
        schema_url='/api/',
    )),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
