
'''
Custom adapter methods for allauth.
See https://django-allauth.readthedocs.io/en/latest/advanced.html#creating-and-populating-user-instances
'''

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import Person, Demographic
from .helpers import get_or_create_person
from datetime import datetime

import logging
logger = logging.getLogger('corpora')


class PersonAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form):

        user = super(PersonAccountAdapter, self).save_user(request, user, form)

        request.user = user
        # Create a People Object with User Information
        person = get_or_create_person(request)

    def is_open_for_signup(self, request):
        return True


class PersonSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):

        user = super(PersonSocialAccountAdapter, self).save_user(
            request, sociallogin, form)

        # Create a People Object with User Information
        request.user = user
        person = get_or_create_person(request)

        if user.birthday or user.gender:
            gender = user.gender

            # We should import the choices from people.models and look up the
            # chars from the tuple strings.
            if 'male' in gender.lower():
                gender = 'M'
            elif 'female' in gender.lower():
                gender = 'F'
            elif 'other' in gender.lower():
                gender = 'O'

            demo = Demographic.objects.create(gender=gender, person=person)
            demo.save()

        # We should try and get demographics from social account - sex,
        # language, etc.

    def populate_user(self, request, sociallogin, data):
        user = super(PersonSocialAccountAdapter, self).populate_user(
            request, sociallogin, data)

        if data.get('sex'):
            gender = data.get('sex')
        elif data.get('gender'):
            gender = data.get('gender')
        else:
            gender = None

        if data.get('birthday'):
            # if provider is facebook, format = MM/DD/YYYY
            birthday = data.get('birthday')
            birthdate = datetime.strptime(birthday, "%m/%d/%Y")
        else:
            birthdate = None

        logger.debug(str(data))

        user.birthday = birthdate
        user.gender = gender
