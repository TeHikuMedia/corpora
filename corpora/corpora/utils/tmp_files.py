
from django.conf import settings
import os
import pwd
import grp
import stat
from subprocess import Popen, PIPE

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
    uid = pwd.getpwnam(settings.APPLICATION_USER).pw_uid
    gid = grp.getgrnam(settings.APPLICATION_GROUP).gr_gid

    BASE = os.path.join(
        '/tmp',
        "{0}_files".format(settings.PROJECT_NAME))

    if not os.path.isdir(BASE):
        os.mkdir(BASE)
        os.chown(BASE, uid, gid)

    if model:
        BASE = os.path.join(
            BASE,
            str(model.__class__.__name__)+str(model.pk))

    # CREATE DIRECTORY IF NO EXIST
    if not os.path.isdir(BASE):
        os.mkdir(BASE)
        try:
            os.chown(BASE, uid, gid)
        except OSError:
            logger.error('COULD NOT CHOWN: {0}'.format(BASE))

    # Check permissions and change?

    return BASE


def erase_all_temp_files(model, test=False, force=False):
    '''
    This medthod requires a model so that you don't accidentally erase
    everything. Include model=None to erase the entire base directory.
    '''

    try:
        import shutil
        shutil.rmtree(get_tmp_stor_directory(model))
    except:
        if force:

            p = Popen(
                ['rm', '-Rf', os.path.join(get_tmp_stor_directory(model), '*')
                 ], stdin=PIPE, stdout=PIPE)

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

    tmp_stor_dir = get_tmp_stor_directory(model)

    paths = [
        get_tmp_stor_directory(),
        tmp_stor_dir]

    for path in paths:
        try:
            os.makedirs(path)
        except OSError as e:
            es = "{0}".format(str(e))
            if 'file exists' in es.lower():
                continue
            else:
                raise e
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                 stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
                 stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)

    tmp_file = os.path.join(
        tmp_stor_dir,
        file.name.split('/')[-1].replace(' ', ''))

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
        code = ['wget', tmp_file, '-O']
    else:
        code = ['cp', file_path, tmp_file]

    p = Popen(code)
    result, error = p.communicate()

    # Turn this off as it's too much output
    try:
        # logger.debug(result[1])
        error = ' '.join([str(i) for i in error])
    except:
        pass
        # logger.debug(result)

    if not os.path.exists(tmp_file) or 'ERROR 404' in error:
        logger.error('ERROR GETTING: ' + tmp_file)
        logger.error(error)
        raise ValueError
    else:
        logger.debug('Downloaded: ' + os.path.abspath(tmp_file))

    # if test:
    logger.debug(
        '\nMEDIA_PATH:\t%s\nTMP_STOR_DIR:\t%s\nTMP_FILE:\t%s\nABS_DIR:\t%s'
        % (file_path, tmp_stor_dir, tmp_file, absolute_directory))

    return file_path, tmp_stor_dir, tmp_file, absolute_directory
