# -*- coding: utf-8 -*-

from django.conf.urls import url, include
# from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

from corpora.views import views
from django.views.generic import RedirectView
# from people.views import profile_redirect
from rest_framework.documentation import include_docs_urls


urlpatterns = [

    url(r'^$', views.home, name='home'),
    url(r'^privacy', views.privacy, name='privacy'),
    url(r'^', include('corpus.urls', namespace='corpus')),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('allauth.urls')),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^signup/',
        RedirectView.as_view(
            permanent=False,
            query_string=True,
            url='/accounts/signup'),
        name='signup'),

    url(r'^login/',
        RedirectView.as_view(
            permanent=False,
            query_string=True,
            url='/accounts/login'),
        name='login'),

    # url(r'^$', cache_on_auth(settings.SHORT_CACHE)(views.home), name='home'),

    url(_(r'^people/'), include('people.urls', namespace='people')),
    # url(r'^people/profile', profile_redirect, name='profile-backwards-comp'),

    # url(r'^$', cache_on_auth(settings.SHORT_CACHE)(views.home), name='home'),

    url(r'^', include('corpora.urls_api', namespace='api')),
    url(r'^docs/', include_docs_urls(title='Corpora API')),

    # url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
    #     name='django.contrib.sitemaps.views.sitemap')

]



# I think it's better we store language preference in cookie and not do url redirects
# urlpatterns += i18n_patterns(
#     url( _(r'^people/'), include('people.urls', namespace='people')),
# )
# prefix_default_language=True