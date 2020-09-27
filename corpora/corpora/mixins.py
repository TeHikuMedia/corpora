# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext as _
from django.contrib.sites.shortcuts import get_current_site

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from people.helpers import get_or_create_person
from django.templatetags.static import static


class SiteInfoMixin(object):
    x_description = _('Description for a particular view')
    x_title = _('Title for your view')
    x_image = static('corpora/img/icon.png')
    x_icon = static('corpora/img/icon.png')

    def get_context_data(self, **kwargs):
        context = super(SiteInfoMixin, self).get_context_data(**kwargs)
        context['x_title'] = self.x_title
        context['x_description'] = self.x_description

        if 'http' not in self.x_image:
            site = get_current_site(self.request)
            self.x_image = 'https://'+site.domain + self.x_image

        if 'http' not in self.x_icon:
            site = get_current_site(self.request)
            self.x_icon = 'https://'+site.domain + self.x_icon

        context['x_image'] = self.x_image
        context['x_icon'] = self.x_icon

        person = get_or_create_person(self.request)

        if hasattr(person, 'groups'):
            groups = person.groups
            if groups.count() == 1:
                group = groups.first()
                person.group = group

        context['person'] = person

        return context


class EnsureCsrfCookieMixin(object):
    """
    Ensures that the CSRF cookie will be passed to the client.
    NOTE:
        This should be the left-most mixin of a view.
    """

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return super(EnsureCsrfCookieMixin, self).get(request, *args, **kwargs)


class CollectStaticOnGetMixin():
    collect_static = False

    def get(self, *args, **kwargs):
        # RUN COLLECT STATIC WHEN WE RUN SERVER!
        if self.collect_static:
            from django.core.management import call_command
            call_command('collectstatic', verbosity=0, interactive=False)

        return super().get(*args, **kwargs)
