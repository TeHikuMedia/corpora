# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages

from transcription.models import \
    Transcription, AudioFileTranscription, TranscriptionSegment

from people.helpers import get_person
from transcription.utils import create_transcription_segments_admin
from transcription.transcribe import transcribe_aft_async


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'corrected_text', 'recording',
                    'word_error_rate', 'updated', )
    date_hierarchy = 'updated'
    raw_id_fields = ('recording',)
    readonly_fields = ('word_error_rate', )
    list_filter = ('recording__language', 'updated',)


@admin.register(AudioFileTranscription)
class AudioFileTranscriptionnAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'audio_file',
                    'uploaded_by', 'updated', 'created', 'ignore')
    actions = ('create_segments', 'transcribe_segments')
    raw_id_fields = ('uploaded_by',)

    def get_changeform_initial_data(self, request):
        person = get_person(request)
        return {'uploaded_by': person.id}

    def create_segments(self, request, queryset):
        for obj in queryset:
            info = create_transcription_segments_admin(obj)
            messages.add_message(
                request, messages.INFO,
                info)

    def transcribe_segments(self, request, queryset):
        for obj in queryset:
            info = transcribe_aft_async.apply_async([obj.pk])
            messages.add_message(
                request, messages.INFO,
                "Runing transcription job {0}.".format(info))


@admin.register(TranscriptionSegment)
class TranscriptionSegmentAdmin(admin.ModelAdmin):
    readonly_fields = ('start', 'end', 'no_speech_detected')
    list_display = ('parent', 'text', 'start', 'end', 'updated', 'no_speech_detected')
    raw_id_fields = ('parent', 'edited_by', 'child',)
