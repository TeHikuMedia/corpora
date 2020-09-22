
from django import template

import logging
logger = logging.getLogger('corpora')

register = template.Library()


@register.filter()
def duration(value):
    value = float(value/100.0)  # convert to seconds

    hours = int(value/(60.0 * 60.0))
    minutes = int((value - hours*60.0*60.0)/60.0)
    seconds = int(value - hours*60.0*60.0 - minutes*60.0)

    if hours == 0:
        return "{0:02d}:{1:02d}".format(minutes, seconds)
    else:
        return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)
