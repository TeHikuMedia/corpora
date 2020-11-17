
from django.conf import settings
import os
import pwd
import grp
import stat
import glob
from subprocess import Popen, PIPE
import tempfile
from boto.s3.connection import S3Connection

import logging
logger = logging.getLogger('corpora')


def get_file_url(f, expires=60):
    s3 = S3Connection(settings.AWS_ACCESS_KEY_ID_S3,
                      settings.AWS_SECRET_ACCESS_KEY_S3,
                      is_secure=True)
    # Create a URL valid for 60 seconds.
    return s3.generate_url(expires, 'GET',
                           bucket=settings.AWS_STORAGE_BUCKET_NAME,
                           key=f.name)


def get_tmp_stor_directory(model=None):
    return tempfile.mkdtemp(prefix=settings.PROJECT_NAME)


def erase_all_temp_files(model, test=False, force=False):
    for path in glob.glob(f'/tmp/{settings.PROJECT_NAME}'):
        p = Popen(['rm', '-Rf', path], stdin=PIPE, stdout=PIPE)
        output, errors = p.communicate()


def prepare_temporary_environment(model, test=False, file_field='audio_file'):
    # This method gets strings for necessary media urls/directories and create
    # tmp folders/files
    # NOTE: we use "media" that should be changed.

    file = getattr(model, file_field)
    absolute_directory = ''

    if 'http' in file.url:
        file_path = file.url
    else:
        file_path = settings.MEDIA_ROOT + file.name

    tempDir = get_tmp_stor_directory()
    tmp_stor_dir = tempDir

    tmp_file = os.path.join(
        tmp_stor_dir,
        file.name.split('/')[-1].replace(' ', ''))

    print(tmp_file)

    if os.path.exists(tmp_file):
        # Ensure permissions are correct.
        try:
            os.chmod(tmp_file, stat.S_IRUSR | stat.S_IWUSR |
                     stat.S_IRGRP | stat.S_IROTH)
        except:
            logger.debug(
                "File {0} exists, can't modify its permissions,\
lets hope this is okay".format(tmp_file))
        return file_path, tmp_stor_dir, tmp_file, absolute_directory

    # Will just replace file since we only doing one encode.
    if 'http' in file_path:
        url = get_file_url(file)
        code = ['wget', file_path, '-O', tmp_file]
    else:
        code = ['cp', file_path, tmp_file]

    p = Popen(code)
    result, error = p.communicate()

    # if test:
    logger.debug(
        '\nMEDIA_PATH:\t%s\nTMP_STOR_DIR:\t%s\nTMP_FILE:\t%s\nABS_DIR:\t%s'
        % (file_path, tmp_stor_dir, tmp_file, absolute_directory))

    return file_path, tmp_stor_dir, tmp_file, absolute_directory
