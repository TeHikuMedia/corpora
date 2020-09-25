# -*- coding: utf-8 -*-
from django.conf import settings
from boto.s3.connection import S3Connection
import subprocess
import os
import tempfile
import errno
import json



class MediaManager():
    '''
    A class that handles manipulation of media objects. A key component of this
    class is that it will write a temp file and use that for manipulation. This
    is beneficial when, for example, media files are stored in remote locations
    such as S3.
    '''

    def __init__(self, django_file_field_object):
        self.file = django_file_field_object
        self.versions = {}
        handle, self.tmp_file = tempfile.mkstemp()

        if 'http' in self.file.url:
            url = self.get_s3_file_url(self.file)
            code = ['wget', url, '-O', self.tmp_file]
        else:
            code = ['cp', settings.MEDIA_ROOT + self.file.name, self.tmp_file]

        # Fetch the original file and write it to tmpfile
        p = subprocess.Popen(code)
        result, errors = p.communicate()
        self.set_media_stats()

    def __del__(self):
        try:
            os.remove(self.tmp_file)
        except:
            pass

        for v in self.versions.keys():
            # Delete old tmp file
            os.remove(self.versions[v]['file_path'])
            try:
                os.rmdir(self.versions[v]['tmp_dir'])
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise e

    def get_s3_file_url(self, f, expires=60):
        s3 = S3Connection(settings.AWS_ACCESS_KEY_ID_S3,
                          settings.AWS_SECRET_ACCESS_KEY_S3,
                          is_secure=True)
        # Create a URL valid for 60 seconds.
        return s3.generate_url(expires, 'GET',
                               bucket=settings.AWS_STORAGE_BUCKET_NAME,
                               key=f.name)

    def get_base_name(self):
        return os.path.basename(self.tmp_file)

    def set_media_stats(self):
        # Probe the file and get its codec

        command = \
            "ffprobe -v quiet -print_format json -show_format -show_streams {0}".format(self.tmp_file)

        p = subprocess.Popen(
            command.split(' '),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        output, errors = p.communicate()
        # logger.debug(self.tmp_file)
        # logger.debug(output)
        # logger.debug(errors)
        data = json.loads(output)

        self.duration = data['format']['duration']
        self.format = data['format']['format_name']
        self.streams = data['streams']

    def convert(self, params, file_extension):
        # Convert audio to wav for faster processing
        base_name = self.get_base_name()
        tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, base_name) + '.' + file_extension

        try:
            ffmpeg_cmd = ["ffmpeg", '-hide_banner', '-loglevel', 'panic',
                          "-y",  # overwrite output files without asking
                          "-i", self.tmp_file] + params + [tmp_file]

            p = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
            output, errors = p.communicate()

        finally:
            # Add new version
            self.versions[file_extension] = {
                'file_path': tmp_file,
                'tmp_dir': tmp_dir
            }

    def convert_to_wave(self):
        # Convert audio to wav for faster processing
        base_name = self.get_base_name()
        tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, base_name) + '.wav'

        params = ['-ac', '1', '-c:a', 'pcm_s16le', '-f', 'wav', '-ar', '16000']
        try:
            ffmpeg_cmd = ["ffmpeg", '-hide_banner', '-loglevel', 'panic',
                          "-y",  # overwrite output files without asking
                          "-i", self.tmp_file] + params + [tmp_file]

            p = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
            output, errors = p.communicate()

        finally:
            # Add new version
            self.versions['wav'] = {
                'file_path': tmp_file,
                'tmp_dir': tmp_dir
            }

    def convert_to_aac(self):
        # Convert audio to aac for faster processing
        # Check if not already aac. if aac, just do easy convert

        base_name = self.get_base_name()
        tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, base_name) + '.m4a'

        codec = 'aac'
        if 'm4a' in self.format or 'mp4' in self.format or 'mov' in self.format:
            for stream in self.streams:
                if 'aac' in stream['codec_name'] and \
                        'audio' in stream['codec_type']:
                    codec = 'copy'

        params = ['-c:a', codec, '-movflags', '+faststart']
        try:
            ffmpeg_cmd = ["ffmpeg", '-hide_banner', '-loglevel', 'panic',
                          "-y",  # overwrite output files without asking
                          "-i", self.tmp_file] + params + [tmp_file]

            p = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
            output, errors = p.communicate()

        finally:
            # Add new version
            self.versions['aac'] = {
                'file_path': tmp_file,
                'tmp_dir': tmp_dir
            }
