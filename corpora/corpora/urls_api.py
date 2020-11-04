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
router.register(r'users', corpora_api.UserViewSet)

router.register(r'qualitycontrol', corpus_api.RecordingQualityControlViewSet)
router.register(r'recordingqualitycontrol', corpus_api.RecordingQualityControlViewSet)
router.register(r'sentencequalitycontrol', corpus_api.SentenceQualityControlViewSet)
router.register(r'sentences', corpus_api.SentenceViewSet)
router.register(r'listen', corpus_api.ListenViewSet, 'listen')
router.register(r'recordings', corpus_api.RecordingViewSet, 'recording')
router.register(r'recording_fetch', corpus_api.RecordingFetchViewSet, 'recording_fetch')
router.register(r'pronunciation_fetch', corpus_api.PronunciationFetchViewSet, 'pronunciation_fetch')

router.register(r'sources', corpus_api.SourceViewSet)
router.register(r'text', corpus_api.TextViewSet)
router.register(r'recordingmetadata', corpus_api.RecordingMetadataViewSet)


router.register(r'tribes', people_api.TribeViewSet)
router.register(r'demographics', people_api.DemographicViewSet)
router.register(r'persons', people_api.PersonViewSet)
router.register(r'profile', people_api.ProfileViewSet)


router.register(r'knownlangauges', people_api.KnownLanguageViewSet)
router.register(r'accept_license', license_api.AcceptLicenseViewSet)

router.register(r'transcriptions', transcription_api.TranscriptionViewSet)
router.register(
    r'transcription-segment', transcription_api.TranscriptionSegmentViewSet)
router.register(
    r'transcription', transcription_api.AudioFileTranscriptionViewSet)


urlpatterns = [

    url(r'^api/sentences/$', corpus_api.SentencesView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include(
        'rest_framework.urls',
        namespace='rest_framework')),
    url(r'^api/magiclogin/$', people_api.MagicLoginView.as_view()),

]

urlpatterns += [
    url(r'^api-token-auth/', views.obtain_auth_token),
]
