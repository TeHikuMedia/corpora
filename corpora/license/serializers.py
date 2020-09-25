from license.models import \
    AcceptLicense

from rest_framework import serializers

from license.models import License, AcceptLicense
from people.helpers import get_person, get_current_language
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from people.models import KnownLanguage

import logging
logger = logging.getLogger('corpora')


class AcceptLicenseSerializer(serializers.HyperlinkedModelSerializer):
    person = serializers.PrimaryKeyRelatedField(read_only=True)
    license = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = AcceptLicense
        fields = ('person', 'license', 'pk')

    def create(self, validated_data):

        person = get_person(self.context['request'])

        language = get_current_language(self.context['request'])
        current_license = License.objects.get(language=language)

        # try:

        #     active = KnownLanguage.objects.get(active=True, person=person)
        #     current_license = License.objects.get(language=active.language)
        # except Exception as e:
        #     current_license = License.objects\
        #         .get(sitelicense__site=settings.SITE_ID)

        accept_license, created = \
            AcceptLicense.objects.get_or_create(person=person)

        accept_license.license.add(current_license)
        accept_license.save()
        return accept_license
