# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from . import parser

from corpus.models import Recording, Sentence, Source, QualityControl
from django.contrib.contenttypes.models import ContentType
import corpus.aggregate as aggregate

from django.core.files import File


class CorpusRecordingTestCase(TestCase):

    def setUp(self):
        # test_short_audio_file = open('test.aac')
        source = Source.objects.create(
            description="Test source.",
            author="Hone Heke",
            source_type="D",
            source_name="Souce"
            )
        sentence = Sentence.objects.create(
            text="He test tēnei.",
            language='mi',
            source=source)
        file = File(
            open('corpora/tests/test.aac'))

        recording = Recording.objects.create(
            audio_file=file,
            sentence=sentence)

        recording2 = Recording.objects.create(
            audio_file=file,
            sentence=sentence)

        recording_ct = ContentType.objects.get_for_model(recording)
        QualityControl.objects.create(
            object_id=recording.pk,
            content_type=recording_ct,
            good=1)
        QualityControl.objects.create(
            object_id=recording.pk,
            content_type=recording_ct,
            good=1)
        QualityControl.objects.create(
            object_id=recording.pk,
            content_type=recording_ct,
            approved=True)
        QualityControl.objects.create(
            object_id=recording.pk,
            content_type=recording_ct,
            bad=1)
        QualityControl.objects.create(
            object_id=recording.pk,
            content_type=recording_ct,
            delete=1)
        QualityControl.objects.create(
            object_id=recording.pk,
            content_type=recording_ct,
            star=3)
        QualityControl.objects.create(
            object_id=recording.pk,
            content_type=recording_ct,
            star=1)

    def test_create_md5_hex(self):
        recording = Recording.objects.first()

        self.assertEqual(
            '069576370ff3d8c4269bdbe31170ee47',
            recording.audio_file_md5)

    def test_build_qualitycontrol_stat_dict(self):
        recording = Recording.objects.first()
        recording2 = Recording.objects.last()
        stats = aggregate.build_qualitycontrol_stat_dict(
            recording.quality_control.all())
        self.assertEqual(stats['approved'], 1)
        self.assertEqual(stats['good'], 2)
        self.assertEqual(stats['bad'], 1)
        self.assertEqual(stats['trash'], 1)
        self.assertEqual(stats['star'], 4)
        self.assertEqual(stats['count'], 7)

        stats = aggregate.build_qualitycontrol_stat_dict(
            recording2.quality_control.all())
        self.assertEqual(stats['approved'], 0)
        self.assertEqual(stats['good'], 0)
        self.assertEqual(stats['bad'], 0)
        self.assertEqual(stats['trash'], 0)
        self.assertEqual(stats['star'], 0)
        self.assertEqual(stats['count'], 0)

    def test_base64_audio_upload(self):
        pass


class CorpusTextTestCase(TestCase):
    def test_get_sentences(self):
        sentences = list(parser.get_sentences(SAMPLE_1))
        # for s in sentences:
        #     print(s.encode('utf-8'))
        self.assertEqual(sentences[0]['sentence'], 'HAKIHEA/TĪHEMA 2017')
        # self.assertEqual(sentences[-1]['sentence'], 'Ka mutu, pēnā he kōrero ā koutou me pēhea te pānui nei e pai ake ai, pēnā he aha rānei ngā mea e hiahia ana koutou kia whakaurua ki ngā pānui o muri atu, tēnā, kōrerotia mai')

        # We're only allowing sentences of certain lengths so this is thr correct eval
        self.assertEqual(sentences[-1]['sentence'], 'TE RŪNANGA NUI O TE AUPŌURI')

    def test_get_sentences_2(self):
        sentences = list(parser.get_sentences(SAMPLE_2))
        self.assertEqual(sentences[0]['sentence'],
                         'Ngā waiata o roto i Ngā Mōteatea')
        self.assertEqual(sentences[2]['sentence'], 'He whakamihi')

    def test_has_english(self):
        self.assertTrue(parser.has_english('Hello my name is Greg'))
        self.assertTrue(parser.has_english('Ōtautahi is my home'))
        self.assertTrue(parser.has_english('Ten songs'))
        self.assertTrue(parser.has_english('Acknowledgements'))
        self.assertTrue(parser.has_english('Bibliography'))
        self.assertTrue(parser.has_english('The songs of Ngā Mōteatea'))

        self.assertFalse(parser.has_english('Ko Kerikori tōku ingoa'))
        self.assertFalse(parser.has_english('Ko Ōtautahi tōku kainga'))
        self.assertFalse(
            parser.has_english('Ngā waiata o roto i Ngā Mōteatea'))
        self.assertFalse(parser.has_english('Ētahi waiata tekau'))
        self.assertFalse(parser.has_english('He whakamihi'))


SAMPLE_1 = """# Source: http://mailchi.mp/deb5e6d2d419/te-karere-a-te-aupuri-88351
# Email / newsletter
# Te Rūnanga Nui o Te Aupōuri
# publish date December 2017
# accessed 8 december 2017
#
#


HAKIHEA/TĪHEMA 2017
Tēnā koutou e te iwi whānui o Te Aupōuri, puta noa.
Tēnā tātou i ō tātou whanaunga kua huri tuara ake nei.
Haere rā e ngā mate ki te okiokinga mutunga kore.
Kāti rā, e ngā uri whakatupu o rātou mā, tēnā tātou katoa.

TE RŪNANGA NUI O TE AUPŌURI
He kaupapa hōu te pānui nei hei whakatuara i ngā kōrero o te pae tukutuku me te whārangi pukamata a te Rūnanga kia mōhio ai koutou, te iwi, ki ngā whakanekenekehanga o tō tātou Rūnanga me tō tātou iwi.  Ka mutu, pēnā he kōrero ā koutou me pēhea te pānui nei e pai ake ai, pēnā he aha rānei ngā mea e hiahia ana koutou kia whakaurua ki ngā pānui o muri atu, tēnā, kōrerotia mai.
"""

SAMPLE_2 = """Ngā waiata o roto i Ngā Mōteatea

The songs of Ngā Mōteatea

Ētahi waiata tekau

Ten songs

He whakamihi

Acknowledgements

Bibliography





He kupu takamua


He kohinga waiata tawhito a Ngā Mōteatea, e whā ngā pukupuka, ko tōna 400 nei ngā waiata o roto, me ngā whakapākehātanga i te taha. Ko Āpirana Ngata te ringa whakaemi, ā, he mea whakaputa ōna wāhanga mai i ngā tau o ngā 1920. Kei ngā waiata nei, tae atu ki ngā kupu whakataki me ngā kupu whakamārama i ngā waiata, tētahi momo matū e ora ai te tangata e hiakai ana ki tēnei mea, ki te mātauranga. Kei konei ngā tohu o tērā umanga onamata a te Māori, o te tito mōteatea, tae atu ki ngā tikanga tito me ngā pūmanawa o ngā kaitito, ngā kaitārai i te kupu kia huatau tonu. Kei konei anō e putu ana ngā kōrero mō te ao Māori — ōna tikanga, ōna whakaaro, ōna whakapono, tae atu ki te āhua o te noho ā-iwi a te Māori i mua, ngā āhuatanga nui i pā, ngā tūpuna rongonui, te takoto o te whenua me ngā taonga tuku iho. Engari he kohinga waiata anō a Ngā Mōteatea kia waiatatia, kia mirimiria kia hāngai ake ki tētahi āhua hou, ā, i ngā wāhi kāore e mōhiotia ana te rangi, kia titoa he puoro hou hei kawe i ngā kupu. Kei ngā kōpae puoro kua tāia hei hoa mō ia wāhanga o te putanga o ngā tau 2004–7 ētahi waiata āhua maha tonu, hei wetewete mā te hinengaro, hei rekareka mā te taringa, mā te ngākau, hei hiki anō mā te reo waiata."""
