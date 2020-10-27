from django.utils.translation import ugettext_lazy as _

from celery import shared_task

from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from corpus.models import Recording, Sentence, Source
from transcription.models import \
    Transcription, TranscriptionSegment, AudioFileTranscription
from corpus.views.views import RecordingFileView
from django.contrib.sites.shortcuts import get_current_site

from corpora.utils.tmp_files import \
    prepare_temporary_environment, \
    erase_all_temp_files, \
    get_tmp_stor_directory

from people.helpers import get_current_known_language_for_person

from transcription.utils import \
    create_and_return_transcription_segments, check_to_transcribe_segment
from corpora.utils.task_management import \
    check_and_set_task_running

from django.core.files import File
import wave
import contextlib
import os
import stat
import ast
import sys
import requests
import json
import uuid
from subprocess import Popen, PIPE
import time


from django.core.cache import cache

import logging
logger = logging.getLogger('corpora')


def parse_sphinx_transcription(lines):
    transcription = []
    new_list = []
    append = False
    for item in lines:
        parts = item.split(" ")
        obj = parts.pop(0)

        for part in parts:
            try:
                float(part)
                append = True
            except:
                append = False
                break
        if append:
            new_list.append(item)
            if obj not in ["<s>", "</s>", "<sil>"] and len(parts) == 3:
                transcription.append(obj)

    text = " ".join(transcription)
    return text


def transcribe_audio_sphinx(
        audio, continuous=False, file_path=None, timeout=32):
    # api_url = "https://waha-tuhi.dragonfly.nz/transcribe"
    # DeepSpeech: http://waha-tuhi-api-17.dragonfly.nz
    API_URL = settings.DEEPSPEECH_URL
    if continuous:
        pass  # not available with deepspeech
        # API_URL = "http://waha-tuhi-api-15.dragonfly.nz/transcribe_continuous"

    # the file_object could be in memory for small files and a temp file for
    # large files. we need to handle this. currently assuming small files
    # in memory
    # https://docs.djangoproject.com/en/2.0/ref/files/uploads/

    if file_path:
        f = open(file_path, 'rb')
        audio = f.read()
        f.close()

    headers = {
        'Accept': 'application/json',
    }

    logger.debug(u'Sending request to {0}'.format(API_URL))

    timeouts = [2, 4, 8, 16, 32]
    tries = 0
    while tries < len(timeouts):

        try:
            response = requests.post(
                API_URL,
                data=audio,
                timeout=timeouts[tries],
                headers=headers)
            logger.debug(u'{0}'.format(response.text))

            result = json.loads(response.text)
            result['API_URL'] = API_URL
            return result

        except requests.exceptions.ConnectTimeout:
            result = {
                'success': False,
                'transcription': 'Could not get a transcription. ConnectTimeout'
            }
        except requests.exceptions.ReadTimeout:
            result = {
                'success': False,
                'transcription': 'Could not get a transcription. ReadTimeout'
            }
        except Exception as e:
            result = {
                'success': False,
                'transcription': 'Unhandled exception. {0}'.format(e)
            }

        tries = tries + 1

    if tries >= timeout:
        logger.debug(result)

    result['API_URL'] = API_URL
    return result


def transcribe_audio_quick(file_object):
    logger.debug('DOING QUICK TRANSCRIPTION')

    tempDir = get_tmp_stor_directory()
    BASE = tempDir
    tmp_file = os.path.join(
        BASE,
        "tmp_file_{0}.{1}".format(
            uuid.uuid4(), file_object.name.split('.')[-1])
        )

    f = open(tmp_file, 'wb')
    for chunk in file_object.chunks():
        f.write(chunk)
    f.close()

    p = Popen(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
         'default=noprint_wrappers=1:nokey=1', tmp_file],
        stdin=PIPE, stdout=PIPE)

    output, errors = p.communicate()
    duration = float(output)

    if duration > 100:
        return {'transcription': 'Stream duration is too long. Not Transcribing.'}

    convert = [
        'ffmpeg', '-y', '-i', tmp_file, '-ar', '16000', '-ac', '1',
        '{0}.wav'.format(tmp_file)]

    post = [
        'curl', '-X', 'POST', '--data-binary', '@{0}.wav'.format(tmp_file),
        '--header', '"Accept: application/json"',
        '--header', '"Content-Type: application/json"',
        settings.DEEPSPEECH_URL]

    p = Popen(convert, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (output, errors) = p.communicate()
    p_status = p.poll()
    while p_status is None:
        p_status = p.poll()

    p = Popen(post, stdout=PIPE)
    (output, errors) = p.communicate()

    p = Popen(['rm', tmp_file])
    p.communicate()
    p = Popen(['rm', '{0}.wav'.format(tmp_file)])
    p.communicate()

    logger.debug(output)
    logger.debug(post)

    return json.loads(output.strip())


# def transcribe_audio(recording, file_object):

#     file_object.open()
#     p = Popen(
#         ['ffmpeg', '-i', '-', '-ar', '16000', '-ac', '1',  '-'],  # '-f', 's16le',
#         stdin=PIPE, stdout=PIPE)

#     output, errors = p.communicate(file_object.read())
#     file_object.close()

#     # result2 = transcribe_audio_sphinx(output, continuous=True)
#     result = transcribe_audio_sphinx(output)

#     recording.sentence_text = result['transcription'].strip()
#     recording.save()
#     if result['success']:

#         # Get or create a source for the API
#         source, created = Source.objects.get_or_create(
#             source_name='Transcription API',
#             author="{0}".format(result['model_version']),
#             source_type='M',
#             source_url=result['API_URL'])

#         # Create a new sentence (because why not though this could blow things up in the future!)
#         # We should only do this if they're using the live demo on the website
#         # This makes sense if a person is reading freely to the machine
#         # But doesn't make sense if someone is uploading a recording from
#         # somewhere else.
#         sentence, created = Sentence.objects.get_or_create(
#             text=result['transcription'].strip())
#         known_language = get_current_known_language_for_person(recording.person)

#         if created:
#             sentence.source = source
#             sentence.language = known_language.language
#             sentence.dialect = known_language.dialect
#             sentence.save()

#         # Create a new transcription
#         transcription = Transcription.objects.create(
#             recording=recording,
#             text=result['transcription'].strip(),
#             source=source)
#         transcription.save()

#     return recording.sentence_text


# @shared_task
# def transcribe_audio_task(recording_id):
#     recording = Recording.objects.get(id=recording_id)
#     response = transcribe_audio(recording, recording.audio_file)
#     return response


@shared_task
def transcribe_segment_async(ts_id):
    ts = TranscriptionSegment.objects.get(pk=ts_id)
    try:
        key = u"xtransseg-{0}".format(ts.pk)
        if check_and_set_task_running(key):
            return "Task already running."
        if not ts.text:
            result = transcribe_segment(ts)
        else:
            return "Segment already has text."
    except Exception as e:
        logger.warn("Failed to transcribe segment {0}.".format(ts.pk))
        logger.warn(e)
        return "{0}".format(e)

    return result


def transcribe_segment(ts):
    if not check_to_transcribe_segment(ts):
        return 'Not transcribing segment. Likely segment too long.'
    try:
        file_path, tmp_stor_dir, tmp_file, absolute_directory = \
            prepare_temporary_environment(ts.parent)
    except Exception as e:
        return "Error creating temporary environment. {0}".format(e)

    tmp_seg_file = tmp_stor_dir + '/ts_{0}.wav'.format(ts.pk)

    command = \
        ['ffmpeg', '-i', tmp_file,
         '-ss', '{0:.2f}'.format(ts.start/100.0),
         '-to', '{0:.2f}'.format(ts.end/100.0),
         '-ar', '16000', '-ac', '1',  # '-f', 's16le',
         tmp_seg_file]

    logger.debug("COMMAND: {0}".format(' '.join(command)))

    p = Popen(command, stdin=PIPE, stdout=PIPE)

    output, errors = p.communicate()
    # result = transcribe_audio_sphinx(output)
    result = transcribe_audio_sphinx(
        None, continuous=True, file_path=tmp_seg_file)

    if result['success']:

        # ts.text = parse_sphinx_transcription(result['transcription'])
        ts.text = result['transcription'].strip()
        result['status'] = 'Done'
        ts.transcriber_log = result
        # Get or create a source for the API
        source, created = Source.objects.get_or_create(
            source_name='Transcription API',
            author="{0}".format(result['model_version']),
            source_type='M',
            source_url=result['API_URL'])

        ts.source = source

        if ts.text is '' or ts.text is ' ':
            ts.no_speech_detected = True

        ts.save()
    else:
        result['status'] = (_('Error'))
        if ts.transcriber_log:
            if 'retry' in ts.transcriber_log.keys():
                ts.transcriber_log.update(result)
                ts.transcriber_log['retry'] = False
            else:
                ts.transcriber_log['retry'] = True
        else:
            ts.transcriber_log = result
        ts.save()

    os.remove(tmp_seg_file)

    return result


@shared_task
def transcribe_aft_async(pk):
    try:
        aft = AudioFileTranscription.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return "No AFT with ID {0} exists.".format(pk)

    try:
        segments = create_and_return_transcription_segments(aft)
    except Exception as e:
        logger.debug(e)

        cache_key = 'aft-{0}-retry-transcribe'.format(pk)
        retry = cache.get(cache_key, 0)
        if retry < 5:
            cache.set(cache_key, retry+1)
            msg = transcribe_aft_async.apply_async([pk], countdown=5)
        else:
            aft.ignore = True
            msg = 'Tried 5 times. Stopping.'
            aft.errors = {'info': 'Tried 5 times to transcibe and no luck.'}
            aft.save()
        try:
            erase_all_temp_files(aft)
        except Exception as e:
            logger.debug('Error erasing files for AFT {0}'.format(pk))
            logger.debug(e)

        return "FAILED. Trying again soon... {0}".format(msg)

    if len(segments) == 0:

        try:
            erase_all_temp_files(aft)
        except Exception as e:
            logger.debug('Error erasing files for AFT {0}'.format(pk))
            logger.debug(e)

        return "ERROR: NO SEGMENTS CREATED for AFT {0}".format(pk)

    results = []
    errors = 0
    for segment in segments:
        if not check_to_transcribe_segment(segment):
            continue
        try:
            transcribe_segment(segment)
        except Exception as e:
            logger.warn(e)
            errors = errors + 1
            logger.warn(
                "Failed to transcribe segment {0}.".format(segment.pk))

    erase_all_temp_files(aft)
    return "Transcribed {0} with {1} errors".format(aft, errors)


def calculate_word_probabilities(metadata):
    words = []
    i = 0
    while i < len(metadata):
        word = ''
        word_probs = []
        start_time = None
        m = metadata[i]
        while m['char'] != ' ':
            if start_time is None:
                start_time = m['start_time']
            word = word + m['char']
            word_probs.append(m['prob'])
            if i+1 >= len(metadata):
                break
            i = i+1
            m = metadata[i]
        words.append({'word': word, 'prob': p_word(word_probs), 'start': start_time})
        i = i+1
    return words


# The probability that a word is incorrect before the nth letter:
def p_not_word(n, probabilities):
    if n == 0:
        return 0
    else:
        return probabilities[n - 1] * p_not_word(n - 1, probabilities)  + \
            (1 - probabilities[n - 1])

# The probability of a word being correctly emitted, given the character
# probabilities:
def p_word(probabilities):
    return 1 - p_not_word(len(probabilities), probabilities)
