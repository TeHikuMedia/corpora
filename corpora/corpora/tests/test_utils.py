# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from django.core.files import File

from corpora.utils import media_functions

from transcription.models import AudioFileTranscription
from people.models import Person

import os


class TestMediaFunctions(TestCase):
    def setUp(self):

        p = Person.objects.create(
            full_name="Test Person")

        aft = AudioFileTranscription.objects.create(
            name="Test Audio 1",
            uploaded_by=p)

        file = open('corpora/tests/test.aac', 'rb')
        aft.audio_file.save('test.m4a', File(file))
        file.close()
        aft.save()

    def test_get_duration_from_model(self):
        aft = AudioFileTranscription.objects.first()
        duration = media_functions.get_media_duration(aft)

        self.assertEqual(round(duration*100)/100, 5.61)
