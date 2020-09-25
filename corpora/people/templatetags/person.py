
from django import template

from people.helpers import get_person as get_person_helper
from people.helpers import get_email

import logging
logger = logging.getLogger('corpora')

register = template.Library()


@register.simple_tag(takes_context=True)
def get_person(context):
    try:
        p = get_person_helper(context['request'])
        p.email = p.email()
        return p
    except:
        return None


@register.filter()
def username(model):
    return model.get_username()


@register.filter()
def email(model):
    return get_email(model)
