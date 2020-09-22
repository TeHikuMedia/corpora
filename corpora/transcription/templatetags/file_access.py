
from django import template
from corpora.utils.tmp_files import get_file_url
import logging
logger = logging.getLogger('corpora')

register = template.Library()


@register.filter()
def access_url(file):
    '''Takes a file object and returns the s3 signed url'''
    if file:
        if 'http' in file.url:
            return get_file_url(file, expires=60*60)
        else:
            return file.url
