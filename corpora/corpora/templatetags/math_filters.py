# -*- coding: utf-8 -*-

from django.conf import settings
from django import template

register = template.Library()


@register.filter()
def divide(value, arg):
    try:
        return value/arg
    except:
        return 0
