from django.utils.translation import ugettext_lazy as _
from django.utils import translation

from people.helpers import get_person, get_or_create_person, get_current_language
from people.models import KnownLanguage
from rest_framework import viewsets, permissions

from license.models import AcceptLicense
from license.serializers import \
    AcceptLicenseSerializer

import logging
logger = logging.getLogger('corpora')


class AcceptLicensePermissions(permissions.BasePermission):
    """
    Only a person can edit his/her own info. This
    involved all info including related models; therefore this persmission
    must work accross all the related hyperlink viewsets. Note that we
    don't require authentication to edit the person's info. This
    allows an anyone using the same device to provide info without
    having to create a login.
    """

    def has_permission(self, request, view):

        return True


    def has_object_permission(self, request, view, obj):

        person = get_person(request)
        if person == obj.person:
            # Only a person can view/edit his/her own data
            return True
        else:
            self.message = _("You're not allowed to view this information.")
            return False


class AcceptLicenseViewSet(viewsets.ModelViewSet):
    """
    Simple API endpoint for GET and POST of a License. License
    is determined by the site and the person is determined by
    the request object. API PUT requires putting a PK for the license
    and the person.
    """
    queryset = AcceptLicense.objects.all()
    serializer_class = AcceptLicenseSerializer
    permission_classes = (AcceptLicensePermissions,)

    def get_queryset(self):
        # person = get_person(self.request)
        queryset = AcceptLicense.objects.all()
        person = get_or_create_person(self.request)
        
        language = get_current_language(self.request)

        queryset = AcceptLicense.objects\
            .filter(person=person)\
            .filter(license__language=language)

        return queryset
