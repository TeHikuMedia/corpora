from __future__ import absolute_import, unicode_literals

from helpers.media_manager import MediaManager

import json
import subprocess
import logging

logger = logging.getLogger('corpora')

def get_media_duration(obj):
    '''
    Returns a media objects duration in seconds. Assumes the object has a
    `audio_file` field
    '''

    M = MediaManager(obj.audio_file)
    M.set_media_stats()

    return float(M.duration)
