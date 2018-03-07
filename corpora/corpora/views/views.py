from django.template.context import RequestContext
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.conf import settings

from people.helpers import get_unknown_languages

from corpus import views

from django.contrib.sites.shortcuts import get_current_site


def home(request):
    if request.user.is_authenticated():
        return redirect('people:profile')
    else:

        context = {
            'request': request,
            'languages': get_unknown_languages(None),
        }

        return render(request, 'corpora/home.html', context)
        # return redirect('account/login')


def privacy(request):
    site = get_current_site(request)
    context = {
        'request': request,
        'languages': get_unknown_languages(None),
        'site': site
    }

    return render(request, 'corpora/privacy.html', context)
