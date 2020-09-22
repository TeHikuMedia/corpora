
from django import template

from people.helpers import get_current_language as get_cur_lang
from people.helpers import get_known_languages as get_known_lang
from people.helpers import get_supported_languages as get_supported

import logging
logger = logging.getLogger('corpora')

register = template.Library()


@register.simple_tag()
def get_current_language(request):
    return get_cur_lang(request)


@register.simple_tag()
def get_known_languages(request):
    return get_known_lang(request.user)


@register.simple_tag()
def get_supported_languages():
    return get_supported()
