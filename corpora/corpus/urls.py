from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url, include
from corpus.views import views
from corpus.views.views import SentenceListView, StatsView, ListenView, PronunciationView
from corpus.views.static import WaveWorker, EncoderWorker, EncoderWorkerWasm

urlpatterns = [
    url(_(r'^record/'), views.record, name='record'),
    url((r'^record/'), views.record_redirect, name='record-backwards-comp'),

    url(_(r'^listen/'), ListenView.as_view(), name='listen'),
    url((r'^listen/'), views.listen_redirect, name='listen-backwards-comp'),

    url(r'^submit_recording/',
        views.submit_recording,
        name='submit_recording'),
    url(r'^failed_submit/', views.failed_submit, name='failed_submit'),
    url(_(r'^sentences/'), SentenceListView.as_view(), name='sentence-list'),

    url(r'^recording-file/(?P<pk>[\d]+)/$',
        views.RecordingFileView.as_view(),
        name='recording_file'),

    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    url(_(r'^pronunciation/'), PronunciationView.as_view(), name='pronunciation'),


    url((r'^workers/waveWorker\.min\.js'), WaveWorker.as_view(), name='waveworker'),
    url((r'^workers/encoderWorker\.min\.js'), EncoderWorker.as_view(), name='encoderworker'),
    url((r'^workers/encoderWorker\.min\.wasm'), EncoderWorkerWasm.as_view(), name='encoderworkerwasm'),
]
