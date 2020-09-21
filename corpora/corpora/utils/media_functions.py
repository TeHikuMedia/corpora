from __future__ import absolute_import, unicode_literals

from corpora.utils.tmp_files import prepare_temporary_environment
import json
import subprocess

def get_media_duration(obj):
    '''
    Returns a media objects duration in seconds. Assumes the object has a
    `audio_file_field`
    '''

    file_path, tmp_stor_dir, tmp_file, absolute_directory = \
        prepare_temporary_environment(obj)

    command = \
        "ffprobe -v quiet -print_format json -show_format -show_streams {0}".format(tmp_file)

    p = subprocess.Popen(
        command.split(' '),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    output, errors = p.communicate()
    data = json.loads(output)

    return float(data['format']['duration'])