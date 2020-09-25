# -*- coding: utf-8 -*-

from django.conf import settings
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_request_url_relative(context):
    request = context['request']
    return request.build_absolute_uri('?')
