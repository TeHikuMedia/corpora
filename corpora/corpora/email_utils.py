# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from premailer import transform, Premailer
from django.test import RequestFactory

import logging
logger = logging.getLogger('company.models')


### taken from http://ozkatz.github.io/getting-e-mail-right-with-django-and-ses.html
class EMail(object):
    """
    A wrapper around Django's EmailMultiAlternatives
    that renders txt and html templates.
    Example Usage:
    >>> email = Email(to='oz@example.com', subject='A great non-spammy email!')
    >>> ctx = {'username': 'Oz Katz'}
    >>> email.text('templates/email.txt', ctx)
    >>> email.html('templates/email.html', ctx)  # Optional
    >>> email.send()
    >>>
    """
    def __init__(self, to, subject, request=None):
        self.to = to
        self.subject = subject
        self._html = None
        self._text = None
        self.request = request

    def _render(self, template, context):
        return render_to_string(template, context)

    def html(self, template, context):
        if not self.request:
            rf = RequestFactory()
            request = rf.get('/')
        else:
            request = self.request
        result = render_to_string(template, context=context, request=request, using=None)
        logger.debug('BASE PATH: {0}'.format(settings.STATIC_ROOT))
        try:
            logger.debug('Trying to transform')
            html = Premailer(result)
            html.base_path=settings.STATIC_ROOT
            self._html = html.transform()
            # self._html = transform(result)
        except:
            logger.debug('Transform failed!')
            result = result.replace('"/static/', '"{0}'.format(settings.STATIC_ROOT))
            html = Premailer(result, base_path=settings.STATIC_ROOT)
            self._html = html.transform()
        logger.debug(html)


    def text(self, template, context):
        self._text = self._render(template, context)

    def send(self, from_addr=None, fail_silently=False):
        try:
            basestring
        except NameError:
            basestring = str
        if isinstance(self.to, basestring):
            self.to = [self.to]
        if not from_addr:
            from_addr = getattr(settings, 'DEFAULT_FROM_EMAIL')
        msg = EmailMultiAlternatives(
            self.subject,
            self._text,
            from_addr,
            self.to
        )
        if self._html:
            msg.attach_alternative(self._html, 'text/html')
        return msg.send(fail_silently)