from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.shortcuts import get_current_site

from django.contrib.contenttypes.models import ContentType

from django.utils import timezone
import datetime

from django.core.files import File
import wave
import contextlib
import os
import stat
import subprocess
import ast
import sys

from django.core.cache import cache

from corpora.utils.tmp_files import prepare_temporary_environment

import logging
logger = logging.getLogger('corpora')


@shared_task
def transcode_audio(app, model, pk):
    model_class = ContentType.objects.get(app_label=app, model=model.lower())

    try:
        obj = model_class.get_object_for_this_type(pk=pk)
    except ObjectDoesNotExist:
        msg = 'Tried to get an object that doesn\'t exist'
        logger.warning(msg)
        return msg

    key = u"xtrans-{0}-{1}".format(pk, "{0}-{1}".format(app, model))

    is_running = cache.get(key)

    result = ''
    if is_running is None:
        if not obj.audio_file_aac:
            is_running = cache.set(key, True, 60*5)
            result = encode_audio(obj)
            cache.set(key, False, 60)
        # if not obj.audio_file_wav:
        #     is_running = cache.set(key, True, 60*5)
        #     result = result + encode_audio(obj, codec='wav')
        #     cache.set(key, False, 60)
        return result

    elif is_running:
        return u"Encoding in progress..."

    return u"Already encoded."


def encode_audio(obj, test=False, codec='aac'):

    codecs = {
        'mp3': ['libmp3lame', 'mp3'],
        'aac': ['aac', 'm4a', 44100, 1],
        'wav': ['pcm_s16le', 'wav', 16000, 1]
    }

    file_path, tmp_stor_dir, tmp_file, absolute_directory = \
        prepare_temporary_environment(obj)

    # If a video doesn't have audio this will fail.
    command = 'ffprobe -v quiet -show_entries stream -print_format json ' + \
              tmp_file
    p = subprocess.Popen(command.split(' '))
    output, error = p.communicate()
    data = ast.literal_eval(output)
    streams = data['streams']

    audio = False
    for stream in streams:
        if stream['codec_type'] in 'audio':
            audio = True

    if audio:
        file_name = obj.get_file_name() + '_x'
        extension = codecs[codec][1]

        if codec in 'wav':
            code = "ffmpeg -i {0} -vn -acodec {1} -ar {2} -ac {3} {4}/{5}.{6}".format(
                tmp_file,
                codecs[codec][0], codecs[codec][2], codecs[codec][3],
                tmp_stor_dir, file_name, extension)
        elif codec in 'aac':
            code = \
                "ffmpeg -i {0} -vn -acodec {1} -ar {5} -ac {6} {7} {2}/{3}.{4}".format(
                    tmp_file, codecs[codec][0], tmp_stor_dir, file_name,
                    extension, codecs[codec][2], codecs[codec][3],
                    "-c:a aac -b:a 64k")  # -profile:a aac_he

        logger.debug('Running: '+code)
        p = subprocess.Popen(code.split(' '))
        output, error = p.communicate()
        logger.debug(output)

        logger.debug(u'FILE FILENAME: \t{0}'.format(file_name))
        if file_name is None:
            file_name = 'audio'

        if 'aac' in codec:
            obj.audio_file_aac.save(
                file_name+'.'+extension,
                File(open(tmp_stor_dir+'/{0}.{1}'.format(
                    file_name, extension))))
        elif 'wav' in codec:
            obj.audio_file_wav.save(
                file_name+'.'+extension,
                File(open(tmp_stor_dir+'/{0}.{1}'.format(
                    file_name, extension))))

        code = 'rm '+tmp_stor_dir+'/{0}.{1}'.format(file_name, extension)
        logger.debug('Running: '+code)
        p = subprocess.Popen(code.split(' '))
        output, error = p.communicate()
        logger.debug(output)

    if not audio:
        logger.debug('No audio stream found.')
        return False

    # Need a better way to check this!
    code = 'rm ' + tmp_file
    p = subprocess.Popen(code.split(' '))
    output, error = p.communicate()
    logger.debug(output)
    logger.debug('Removed tmp file %s' % (tmp_file))

    code = 'rm -r ' + tmp_stor_dir
    p = subprocess.Popen(code.split(' '))
    output, error = p.communicate()
    logger.debug(output)
    logger.debug('Removed tmp stor dir %s' % (tmp_stor_dir))

    set_s3_content_deposition(obj)

    return "Encoded {0}".format(obj)


@shared_task
def set_s3_content_deposition(obj):
    import mimetypes

    if 's3boto' in settings.DEFAULT_FILE_STORAGE.lower():

        from boto.s3.connection import S3Connection
        c = S3Connection(
            settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        b = c.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)  # , validate=False)

        attrs = ['audio_file', 'audio_file_aac']
        for attr in attrs:
            file = getattr(obj, attr)
            if file:

                k = file.name
                key = b.get_key(k)  # validate=False)

                if key is None:
                    return "Error: key {0} doesn't exist in S3.".format(key)
                else:
                    metadata = key.metadata
                    metadata['Content-Disposition'] = \
                        "attachment; filename={0}".format(
                            file.name.split('/')[-1])
                    metadata['Content-Type'] = \
                        mimetypes.guess_type(file.url)[0]
                    key.copy(
                        key.bucket,
                        key.name,
                        preserve_acl=True,
                        metadata=metadata)
        return metadata

    else:
        return 'Non s3 storage - not setting s3 content deposition.'
