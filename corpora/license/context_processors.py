from license.models import SiteLicense, License
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from people.helpers import get_or_create_person
from people.models import KnownLanguage


def license(request):
    person = get_or_create_person(request)
    try:
        active = KnownLanguage.objects.get(active=True, person=person)
        license = License.objects.get(language=active.language)
    except ObjectDoesNotExist:
        try:
            sl = SiteLicense.objects.get(site=get_current_site(request))
            license = sl.license
        except:
            license = None
    except:
        license = None
    if license:
        return {'license': license}
    else:
        return {}
