from license.models import SiteLicense
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


def site(request):
    try:
        site = get_current_site(request)
        return {'site': site}
    except:
        return {}
