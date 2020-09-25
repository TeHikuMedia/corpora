# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext_lazy as _

from celery import shared_task

from corpora.utils.tmp_files import \
    prepare_temporary_environment, \
    get_tmp_stor_directory

from transcription.models import \
    TranscriptionSegment, AudioFileTranscription

from subprocess import Popen, PIPE


from wahi_korero import default_segmenter
from wahi_korero import Segmenter
import ast
import json
import time
import os
from django.core.files import File

from django.core.files.base import ContentFile

import logging
logger = logging.getLogger('corpora')


def dummy_segmenter(audio_file_path):
    MIN_DURATION = 4*100
    MAX_DURATION = 10*100

    code = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {0}".format(
        audio_file_path)

    p = Popen(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
         'default=noprint_wrappers=1:nokey=1', audio_file_path],
        stdin=PIPE, stdout=PIPE)

    output, errors = p.communicate()

    duration = float(output)*100  # Milliseconds
    logger.debug("DURATION: {0:.2f}".format(duration))
    logger.debug("SEGMENTS:\n")
    segments = []
    time = 0
    while (time + MAX_DURATION) < duration:
        dt = MAX_DURATION + time
        segments.append({
            'start': time,
            'end': dt,
            'duration': MAX_DURATION})
        logger.debug("{0:04.2f}, {1:04.2f}".format(time/100, dt/100))
        time = time + MAX_DURATION

    segments.append({
            'start': time,
            'end': duration,
            'duration': MAX_DURATION})

    if len(segments) > 1:
        last_chunk = segments[-1]
        if last_chunk['end'] - last_chunk['start'] < MIN_DURATION:
            segments.pop()
            segments.pop()
            segments.append({
                'start': time-MAX_DURATION,
                'end': duration,
                'duration': MAX_DURATION
            })

        tt = segments[-1]
        logger.debug("{0:04.2f}, {1:04.2f}".format(tt['start']/100, tt['end']/100))

    return segments


def slice_audio(aft, start, stop):
    try:
        file_path, tmp_stor_dir, tmp_file, absolute_directory = \
            prepare_temporary_environment(aft)
    except Exception as e:
        return "Error creating temporary environment. {0}".format(e)

    tmp_seg_file = tmp_stor_dir + '/sliced_{0}_{1}.wav'.format(
        start, stop)

    command = \
        ['ffmpeg', '-i', tmp_file,
         '-ss', '{0:.2f}'.format(start/100.0),
         '-to', '{0:.2f}'.format(stop/100.0),
         # '-ar', '16000', '-ac', '1',  # '-f', 's16le',
         tmp_seg_file]

    logger.debug("COMMAND: {0}".format(' '.join(command)))

    p = Popen(command, stdin=PIPE, stdout=PIPE)

    output, errors = p.communicate()

    return tmp_seg_file


def long_audio_segmenter(aft, duration):

    # We'll need to cut up audio and then segment it
    files = []
    slice_length = 10*60*100
    for i in range(int(duration/slice_length)+1):
        start = i*slice_length
        end = start+slice_length
        if end > duration:
            end = duration

        files.append(slice_audio(aft, start, end))

    captioned = []

    count = 0.0
    for file in files:
        offset = count*slice_length
        this_segments = wahi_korero_segmenter(file, offset=offset/100.0)
        captioned = captioned + this_segments
        count = count+1

    return captioned


def long_audio_segmenter_2(aft, duration):

    # We'll need to cut up audio and then segment it
    files = []
    slice_length = 10*60*100
    for i in range(int(duration/slice_length)+1):
        start = i*slice_length
        end = start+slice_length
        if end > duration:
            end = duration

        files.append(slice_audio(aft, start, end))

    captioned = []

    count = 0.0
    for file in files:
        offset = count*slice_length
        this_segments = captioning_segmenter(file, offset=offset)
        captioned = captioned + this_segments
        count = count+1

    return captioned


def wahi_korero_segmenter(file_path, aft=None, offset=0):
    MIN_DURATION = 2*100

    p = Popen(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
         'default=noprint_wrappers=1:nokey=1', file_path],
        stdin=PIPE, stdout=PIPE)

    output, errors = p.communicate()
    duration = float(output)*100  # Hundreths of a second

    # Don't need to do this for short recordings!
    if duration < 10*100:
        return dummy_segmenter(file_path)
    elif duration > 10*60*100:
        return long_audio_segmenter(aft, duration)

    segmenter = default_segmenter()
    segmenter.enable_captioning(caption_threshold_ms=50, min_caption_len_ms=None)
    stream = segmenter.segment_stream(file_path, output_audio=False)  # outputs "captioned" segments    
    segs = [
        {'start': seg[0]+offset,
         'end': seg[1]+offset,
         'duration': (seg[1]-seg[0])
         } for seg, audio in stream]  # 

    logger.debug(segs)

    captioned_for_real = []
    end = None
    while segs:
        seg = segs.pop(0)
        if end:
            start = end
        else:
            start = float(seg['start'])*100
        d = float(seg['duration'])*100

        while abs(int(d/100)) < int(MIN_DURATION/100):
            if segs:
                seg = segs.pop(0)
                d = d + float(seg['duration'])*100
            else:
                logger.debug('MOVING BACKWARDS')
                new_seg = captioned_for_real.pop()
                end = float(seg['end'])*100
                start = new_seg['start']
                d = end - start
                logger.debug("SEG:\t{0: 5.1f} {1: 5.1f}".format(start, end))
                logger.debug("DUR:\t{0: 3.1f}".format(d))

        end = start + d
        captioned_for_real.append({'start': start, 'end': end, 'duration': d})
        logger.debug(("SEG:\t{0: 6.1f} {1: 4.1f}").format(start/100, d/100))

    # for seg in segs:
    #     seg['start'] = float(seg['start'])*100
    #     seg['end'] = float(seg['end'])*100
    #     seg['duration'] = float(seg['duration'])*100
    return captioned_for_real


def captioning_segmenter(file_path, aft=None, offset=0):
    config = {
        'frame_duration_ms': 20,
        'threshold_silence_ms': 40,
        'threshold_voice_ms': 40,
        'buffer_length_ms': 400,
        'aggression': 3,
        'squash_rate': 400
    }

    p = Popen(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
         'default=noprint_wrappers=1:nokey=1', file_path],
        stdin=PIPE, stdout=PIPE)

    output, errors = p.communicate()
    duration = float(output)*100  # Hundreths of a second

    # Don't need to do this for short recordings!
    if duration < 10*100:
        return dummy_segmenter(file_path)
    elif duration > 10*60*100:
        return long_audio_segmenter_2(aft, duration)

    segmenter = Segmenter(**config)

    segmenter.enable_captioning(
        caption_threshold_ms=10,
        min_caption_len_ms=3400
    )

    # tmp_dir = get_tmp_stor_directory(aft)

    # segmenter.segment_audio(file_path, 'tmp_dir', output_audio=False)
    stream = segmenter.segment_stream(file_path, output_audio=False)
    captioned_for_real = []
    for seg, audio in stream:
        start, end = seg
        d = end - start
        captioned_for_real.append({
            'start': start*100+offset,
            'end': end*100+offset,
            'duration': d*100})

    return captioned_for_real


def create_caption_segments(file_path):

    config = {
        'frame_duration_ms': 20,
        'threshold_silence_ms': 40,
        'threshold_voice_ms': 40,
        'buffer_length_ms': 400,
        'aggression': 3,
        'squash_rate': 4000
    }

    segmenter = Segmenter(**config)

    segmenter.enable_captioning(
        caption_threshold_ms=10,
        min_caption_len_ms=3400
    )

    stream = segmenter.segment_stream(file_path, output_audio=False)
    captioned_for_real = []
    for seg, audio in stream:
        start, end = seg
        captioned_for_real.append({
            'start': start*100,
            'end': end*100,
            'duration': (end-start)*100,
            })

    return captioned_for_real


def create_transcription_segments_admin(aft):
    try:
        ts = create_and_return_transcription_segments(aft)
    except Exception as e:
        return "{0}".format(e)

    return "Created {0} segments from {1}".format(len(ts), aft.name)


def convert_audio_file_if_necessary(aft):
    file_path, tmp_stor_dir, tmp_file, absolute_directory = \
        prepare_temporary_environment(aft)

    # Check if file exists
    # Or is something else deleting stuff???
    max_loop = 0
    while not os.path.exists(tmp_file) and max_loop < 30:
        # Might need to wait for the filesystem if we just downlaoded a large file?
        time.sleep(1)
        max_loop = max_loop + 1
        if max_loop == 15:
            file_path, tmp_stor_dir, tmp_file, absolute_directory = \
                prepare_temporary_environment(aft)

    #  Check that audio is in the right format
    command = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', '-show_streams', tmp_file]
    p = Popen(command, stdin=PIPE, stdout=PIPE)
    output, errors = p.communicate()
    results = ast.literal_eval(output)
    convert = False
    for stream in results['streams']:
        if stream["codec_type"] in 'audio':
            if stream["codec_name"] not in "aac mp3 wav":
                convert = True
            if stream["channels"] > 2:
                convert = True

    if convert:
        new_file = '.'.join(tmp_file.split('.')[:-1]) + '.m4a'
        logger.debug(new_file)
        command = [
            'ffmpeg', '-i', tmp_file, '-ar', '44100', '-ac', '1',
            '-c:a', 'aac', new_file]

        logger.debug(command)
        p = Popen(command, stdin=PIPE, stdout=PIPE)
        output, errors = p.communicate()
        if not errors:
            aft.audio_file.save(new_file.split('/').pop(), File(open(new_file)))
            aft.save()
            # f.close()


def create_and_return_transcription_segments(aft):
    '''
    Creates the transcription segments from an AudioFileTranscription model.
    If there's an error this returns an empty list.
    '''
    try:
        convert_audio_file_if_necessary(aft)
    except:
        # If this fails, let's assume that wahi_korero will handle
        # the audio format stuff because it does!
        pass

    # We should delete all segments if we're going to create more!
    deleted = TranscriptionSegment.objects.filter(parent=aft).delete()

    file_path, tmp_stor_dir, tmp_file, absolute_directory = \
        prepare_temporary_environment(aft)

    # This sometimes fails. Not hadnling exceptions here so that
    # we can get debug info in the celery flower task UI.
    segments = create_caption_segments(tmp_file)

    # segments = dummy_segmenter(tmp_file)

    logger.debug(segments)

    ts_segments = []
    for segment in segments:

        start = segment['start']
        end = segment['end']

        ts, created = TranscriptionSegment.objects.get_or_create(
            start=start,
            end=end,
            parent=aft,
            transcriber_log=json.dumps(
                {'status': unicode(_('Waiting'))}))

        ts_segments.append(ts)
    return ts_segments


@shared_task
def compile_aft(aft_pk):
    aft = AudioFileTranscription.objects.get(pk=aft_pk)
    ts = TranscriptionSegment.objects\
        .filter(parent=aft)\
        .order_by('start')

    if not aft.original_transcription:
        logger.debug('NEED TO COMPILE FILE')
        compile_original = True
    else:
        compile_original = False

    transcriptions = []
    original_transcriptions = []
    for t in ts:
        if t.corrected_text:
            transcriptions.append(t.corrected_text.strip())
        if t.text and compile_original:
            original_transcriptions.append(t.text.strip())

    aft.transcription = " ".join(transcriptions)

    if compile_original:
        original_transcription = " ".join(original_transcriptions)
        f = ContentFile(original_transcription)
        aft.original_transcription.save('original.txt', f)

    aft.save()


def check_to_transcribe_segment(ts):
    if ts.end - ts.start > 60*100:
        ts.text = '[Segment too long to transcribe.]'
        ts.corrected_text = '[Segment too long to transcribe.]'
        ts.transcriber_log = {
            'retry': False,
            'message': 'Segment too long to transcribe.'
        }
        ts.save()
        return False
    else:
        return True


def get_duration_components(duration):
    h = int(duration/(100*60*60))
    m = int((duration - h*(100*60*60))/(100*60))
    s = int((duration - h*(100*60*60) - m*(100*60))/(100))
    l = int((duration - h*(100*60*60) - m*(100*60) - s*100))

    return (h, m, s, l)


@shared_task
def build_vtt(aft):
    if type(aft) == str or type(aft) == int:
        aft = AudioFileTranscription.objects.get(pk=aft)

    segments = TranscriptionSegment.objects\
        .filter(parent=aft)\
        .order_by('start')

    data = []
    data.append('WEBVTT')
    data.append('')

    count = 1
    for segment in segments:
        if segment.corrected_text is None:
            if segment.text is None:
                continue
            segment.corrected_text = segment.text

        data.append(str(count))
        count = count + 1
        (sh, sm, ss, sl) = get_duration_components(segment.start)
        (eh, em, es, el) = get_duration_components(segment.end)
        data.append(
            '{0:02d}:{1:02d}:{2:02d}.{3:03d} --> {4:02d}:{5:02d}:{6:02d}.{7:03d}'
            .format(sh, sm, ss, sl, eh, em, es, el)
            )
        data.append(segment.corrected_text)
        data.append('')

    return '\n'.join(data)
