# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from corpora.views import api as corpora_api
from corpus.views import api as corpus_api
from people.views import api as people_api
from license.views import api as license_api
from transcription.views import api as transcription_api
from rest_framework import routers
from rest_framework.authtoken import views


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


urlpatterns = [

    # url(r'^api/sentences/$', corpus_api.SentencesView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include(
        'rest_framework.urls',
        namespace='rest_framework')),

]

urlpatterns += [
    url(r'^api-token-auth/', views.obtain_auth_token),
]


# urlpatterns += [
#     url(r'^docs/', include_docs_urls(
#         title='koreromaori.io API',
#         public=False,
#     )),
# ]

# patterns=[url(r'^api/', include(router.urls))]


