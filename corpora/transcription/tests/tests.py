# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from django.core.files import File

from transcription.transcribe import parse_sphinx_transcription
from transcription.utils import create_and_return_transcription_segments
from transcription.models import AudioFileTranscription

from people.models import Person


import logging
logger_test = logging.getLogger('django.test')


# To do, write these to files.
sample_1 = ["wharenui", "<s> 0.150 0.180 1.000000", "wharenui 0.190 0.940 1.000000", "te whakahokinga tapoko hoa ko te matakawa tuatahi ki te t\u016b ki ng\u0101 manu k\u014drero", "<s> 1.380 1.560 1.000200", "<sil> 1.570 1.930 1.000300", "te 1.940 2.060 0.735330", "whakahokinga 2.070 2.730 0.988565", "tapoko 2.740 3.160 0.019342", "hoa 3.170 3.950 0.118144", "ko 3.960 4.090 0.734522", "te 4.100 4.210 0.986096", "matakawa 4.220 4.900 0.064048", "tuatahi 4.910 5.490 0.867000", "<sil> 5.500 5.740 0.583820", "ki 5.750 5.880 0.937717", "te 5.890 6.040 0.952938", "t\u016b 6.050 6.370 0.673784", "ki 6.380 6.590 0.976967", "ng\u0101 6.600 6.760 0.989059", "manu 6.770 6.980 0.048760", "k\u014drero 6.990 7.430 0.455121", "</s> 7.440 7.800 1.000000", "\u0101kona", "<s> 9.070 9.150 1.000000", "\u0101kona 9.160 9.990 1.000000", ""]
sample_2 = ["n\u014du ana h\u016b o", "<s> 0.000 0.020 1.000100", "n\u014du 0.030 0.440 0.004398", "ana 0.450 0.720 0.055808", "h\u016b 0.730 1.100 0.914928", "o 1.110 1.210 0.931734", "<sil> 1.220 1.550 1.000000", "<sil> 1.560 2.100 1.000000", "<sil> 2.110 2.540 1.000000", "</s> 2.550 2.940 1.000000", "uuuu", "<s> 4.050 4.170 1.000000", "uuuu 4.180 4.660 0.005311", "</s> 4.670 5.050 1.000000", "he kaha te mataika he t\u0101taritia te awa ko t\u014dna wh\u0101nau", "<s> 5.050 5.630 1.000200", "he 5.640 5.800 0.716528", "kaha 5.810 6.140 0.398038", "te 6.150 6.250 0.630178", "mataika 6.260 6.960 0.067901", "he 6.970 7.120 0.313068", "t\u0101taritia 7.130 7.870 0.810321", "te 7.880 8.080 0.973553", "awa 8.090 8.610 0.951509", "ko 8.620 8.750 0.956662", "t\u014dna 8.760 9.150 0.996904", "wh\u0101nau 9.160 9.910 1.000000", ""]
sample_3 = ["reira nui-\u0101-rua tuia tuia h\u016b", "<s> 0.230 0.280 0.999500", "reira 0.290 0.610 0.011811", "nui-\u0101-rua 0.620 1.650 0.135426", "tuia 1.660 2.130 0.583003", "tuia 2.140 2.570 0.588863", "h\u016b 2.580 3.020 1.000000", "kia m\u014dhio te ko waku rohi he hoa kua m\u0101rama k\u014dtou te manu", "<s> 3.510 3.570 1.000100", "kia 3.580 3.830 0.784406", "m\u014dhio 3.840 4.270 0.966568", "te 4.280 4.430 0.983634", "ko 4.440 4.560 0.012513", "waku 4.570 4.920 0.005912", "rohi 4.930 5.360 0.001772", "<sil> 5.370 5.730 0.999500", "<sil> 5.740 6.090 0.999400", "he 6.100 6.230 0.352988", "hoa 6.240 6.570 0.264146", "kua 6.580 6.690 0.175643", "m\u0101rama 6.700 7.200 0.635367", "k\u014dtou 7.210 7.600 0.087468", "te 7.610 7.720 0.462185", "manu 7.730 8.040 0.897706", "</s> 8.050 8.430 1.000000", "te tatangi mai roto", "<s> 8.580 8.640 1.000000", "te 8.650 8.780 0.294775", "tatangi 8.790 9.240 0.031597", "mai 9.250 9.570 0.996705", "roto 9.580 9.840 0.994912", "</s> 9.850 9.980 1.000000", ""]
sample_4 = ["aihe", "<s> 0.000 0.020 0.999900", "aihe 0.030 0.400 0.006329", "</s> 0.410 0.550 1.000000", "ka m\u014dhio koutou ki te patu", "<s> 0.540 0.560 1.000000", "ka 0.570 0.620 0.689807", "m\u014dhio 0.630 0.990 0.998801", "koutou 1.000 1.310 0.238433", "ki 1.320 1.430 0.862761", "te 1.440 1.560 0.964926", "patu 1.570 2.670 1.000000", "a ha", "<s> 4.120 4.230 0.999800", "a 4.240 4.290 0.001030", "ha 4.300 4.670 0.111375", "</s> 4.680 5.110 1.000000", "\u0101", "<s> 5.790 5.870 0.999800", "\u0101 5.880 6.220 0.964347", "<sil> 6.230 6.560 1.000000", "<sil> 6.570 6.900 1.000000", "</s> 6.910 7.310 1.000000", "", "<s> 7.780 8.020 1.000000", "</s> 8.030 8.470 1.000000", "ko aua reo mahara", "<s> 8.850 8.910 1.000000", "ko 8.920 9.030 0.407749", "aua 9.040 9.180 0.433399", "reo 9.190 9.490 1.000000", "mahara 9.500 9.990 1.000000", ""]
# sample_5 = ["ng\u0101 whakatipuranga h\u014du ki te whakaora me t\u014d t\u0101tou m\u0101oritanga \u014d whanaunga t\u0113n\u0101 koutou", "<s> 0.000 0.020 0.999800", "ng\u0101 0.030 0.120 0.984618", "whakatipuranga 0.130 1.030 0.701355", "h\u014du 1.040 1.480 0.082754", "ki 1.490 1.610 0.802017", "te 1.620 1.740 0.922185", "whakaora 1.750 2.570 0.708830", "me 2.580 2.660 0.536831", "t\u014d 2.670 2.830 0.989257", "t\u0101tou 2.840 3.190 0.864402", "m\u0101oritanga 3.200 3.780 1.000000", "\u014d 3.790 4.240 0.416486", "<sil> 4.250 4.520 0.992031", "whanaunga 4.530 5.220 0.969278", "<sil> 5.230 5.650 0.999400", "t\u0113n\u0101 5.660 5.960 0.984322", "koutou 5.970 6.650 1.000000", "t\u0113n\u0101 koutou t\u0113n\u0101 koutou katoa", "<s> 6.780 6.840 1.000200", "t\u0113n\u0101 6.850 7.120 0.941475", "koutou 7.130 7.480 1.000100", "<sil> 7.490 7.690 0.791895", "<sil> 7.700 8.000 0.911731", "t\u0113n\u0101 8.010 8.260 0.585633", "koutou 8.270 8.500 0.973845", "katoa 8.510 8.890 1.000000", "<sil> 8.900 9.670 1.000000", "<sil> 9.680 10.060 1.000000", "<sil> 10.070 10.410 1.000000", "</s> 10.420 10.480 1.000000", ""]


asr_wer = \
    ((u'Te 22 o ngā rā o Ākuhata 1898',
      u'te rua tekau mā rua o ngā rā o ākuhata kotahi mano waru rau iwa tekau mā waru'),
     (u'11 o ngā rā Hepetema 1875',
      u'tekau mā tahi o ngā rā hepetema kotahi mano waru rau whitu tekau mā rima'),
     (u'Whakarongo mai ki te reo irirangi o te hiku o te ika 97.1',
      u'whakarongo mai ki te reo irirangi o te hiku o te ika iwa tekau mā whitutahi'),
     (u'1, 2, 3, 45, 100, 1000, 537, 9375',
      u'tahi rua toru whā tekau mā rima kotahi rau kotahi mano rima rau toru tekau mā whitu iwa mano toru rau whitu tekau mā rima'))


class TestTranscribeMethods(TestCase):
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

    def test_parse_spinx_transcription(self):
        result = parse_sphinx_transcription(sample_1)
        self.assertEqual(
            result,
            "wharenui te whakahokinga tapoko hoa ko te matakawa tuatahi ki te t\u016b ki ng\u0101 manu k\u014drero \u0101kona")

        result = parse_sphinx_transcription(sample_2)
        self.assertEqual(
            result,
            "n\u014du ana h\u016b o uuuu he kaha te mataika he t\u0101taritia te awa ko t\u014dna wh\u0101nau")

        result = parse_sphinx_transcription(sample_3)
        self.assertEqual(
            result,
            "reira nui-\u0101-rua tuia tuia h\u016b kia m\u014dhio te ko waku rohi he hoa kua m\u0101rama k\u014dtou te manu te tatangi mai roto")

        result = parse_sphinx_transcription(sample_4)
        self.assertEqual(
            result,
            "aihe ka m\u014dhio koutou ki te patu a ha \u0101 ko aua reo mahara")

        # result = parse_sphinx_transcription(sample_5)
        # self.assertEqual(
        #     result,
        #     "aihe ka m\u014dhio koutou ki te patu a ha \u0101 ko aua reo mahara")

    def test_create_and_return_transcription_segments(self):

        aft = AudioFileTranscription.objects.first()

        ts = create_and_return_transcription_segments(aft)


class TestWERCalculatio(TestCase):

    def test_wer_calculation(self):
        from transcription.wer.wer import word_error_rate
        from transcription.wer.mi import clean_text_for_wer_calculation

        for item in asr_wer:
            logger_test.debug(clean_text_for_wer_calculation(item[0]))
            logger_test.debug(item[1])
            self.assertEqual(0, word_error_rate(item[0], item[1], 'mi'))

