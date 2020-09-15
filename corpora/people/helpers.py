# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils import translation
from django.conf import settings

from corpus.base_settings import \
    LANGUAGES, LANGUAGE_DOMAINS

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from .models import Person, KnownLanguage

from allauth.account.models import EmailAddress
from rest_framework.authentication import TokenAuthentication
from reo_api.authentication import ApplicationAPITokenAuthentication
from django.contrib.auth.models import AnonymousUser 
import logging
logger = logging.getLogger('corpora')


def get_user(request):
    user = request.user
    # logger.debug("GET USER? {0}".format(user))
    if user is None or user.is_anonymous:
        try:
            token_auth = TokenAuthentication()
            user, token = token_auth.authenticate(request)
            # logger.debug('get user from token, {0} {1}'.format(user, token))
        except:
            pass

    # If we're using an AppToken, return an anonymous user
    try:
        token_auth = ApplicationAPITokenAuthentication()
        AppUser, token = token_auth.authenticate(request)
        if AppUser:
            # logger.debug("SET ANON USER {0}".format(AnonymousUser()))
            return AnonymousUser()
    except:
        pass           

    return user


def get_or_create_person(request):
    user = get_user(request)

    if user.is_anonymous:
        # Check if a session cookie exists
        uuid = request.get_signed_cookie('uuid', None)

        if uuid is not None:
            # get person from uuid
            person, created = Person.objects.get_or_create(uuid=uuid)
            if created:
                logger.info("Created new person, {0}".format(person))
        else:
            # Create person and set uuid
            person = Person.objects.create()
        request.session['uuid'] = person.uuid
    else:
        try:
            person = Person.objects.get(user=user)
        except ObjectDoesNotExist:
            uuid = request.get_signed_cookie('uuid', None)
            if uuid is not None:
                person = Person.objects.get(uuid=uuid)
                if person.user is not None:
                    if person.user is not user:
                        # Another user has signed in
                        # and this user needs a person!
                        person = Person.objects.create(user=user)
                else:
                    person.user = user
            else:
                person = Person.objects.create(user=user)
            first = '' if not user.first_name else user.first_name
            last = '' if not user.last_name else user.last_name
            if first == '' and last == '':
                full_name = user.username
            else:
                full_name = '{0} {1}'.format(first, last)
            if not person.full_name:
                person.full_name = full_name
            person.save()
        request.session['uuid'] = person.uuid

    if person:
        try:
            person.last_user_agent = request.META['HTTP_USER_AGENT']
            person.save()
        except:
            pass

    return person


def get_person(request):
    user = get_user(request)

    if user.is_anonymous:
        # Check if a session cookie exists
        uuid = request.get_signed_cookie('uuid', None)
        if uuid is not None:
            # get person from uuid
            try:
                person = Person.objects.get(uuid=uuid)
            except ObjectDoesNotExist:
                return None
        else:
            return None
    else:
        try:
            person = Person.objects.get(user=user)
        except ObjectDoesNotExist:
            uuid = request.get_signed_cookie('uuid', None)
            if uuid is not None:
                person = Person.objects.get(uuid=uuid)
                person.user = user
            else:
                return None
            person.save()

    if person:
        try:
            person.last_user_agent = request.META['HTTP_USER_AGENT']
            person.save()
        except:
            pass

    return person


def set_language_cookie(response, language):
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=2*365 * 24 * 60 * 60,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE or None
    )
    return response


def set_current_language_for_person(person, language):
    # First, deactivate active languages
    active = KnownLanguage.objects.filter(person=person)
    for kl in active:
        kl.active = False
        kl.save()

    try:
        kl = KnownLanguage.objects.get(person=person, language=language)
    except ObjectDoesNotExist:
        kl = KnownLanguage.objects.create(person=person, language=language)
    finally:
        kl.active = True
        kl.save()

    translation.activate(language)


def get_current_language(request):
    language = translation.get_language()
    person = get_or_create_person(request)
    try:
        active_language = \
            KnownLanguage.objects.get(person=person, active=True)
        return active_language.language
    except ObjectDoesNotExist:
        domain = request.META['SERVER_NAME']
        try:
            language = LANGUAGE_DOMAINS[domain]
        except KeyError:
            language = settings.LANGUAGE_CODE
        return language
    except MultipleObjectsReturned:
        active_language = \
            KnownLanguage.objects.filter(person=person, active=True).first()
        return active_language.language


def get_current_known_language_for_person(person):
    try:
        active_language = \
            KnownLanguage.objects.get(person=person, active=True)
        return active_language

    except ObjectDoesNotExist:
        return None


def get_num_supported_languages():
    return len(LANGUAGES)


def get_known_languages(person):
    if not isinstance(person, Person):
        try:
            person = Person.objects.get(user=person)
        except:
            return None
    ''' Returns a list of language codes known by person '''
    known_languages = \
        [i.language for i in KnownLanguage.objects.filter(person=person)]
    return known_languages


def get_unknown_languages(person):
    if isinstance(person, User):
        try:
            person = Person.objects.get(user=person)
        except:
            person = None
    else:
        person = None

    if person is None:
        known_languages = []
    else:
        ''' Returns a list of language codes not known by person '''
        known_languages = \
            [i.language for i in KnownLanguage.objects.filter(person=person)]

    alter_choices = []
    for i in range(len(LANGUAGES)):
        if LANGUAGES[i][0] not in known_languages:
            alter_choices.append(LANGUAGES[i][0])
    return alter_choices


def get_email(person):
    '''This method looks for and returns a verified email. If no verified email
    exists, then the next available email is returned.'''

    if person.user:
        try:
            email = EmailAddress.objects.get(user=person.user, verified=True)
            return email.email
        except ObjectDoesNotExist:
            try:
                email = EmailAddress.objects.get(user=person.user)
                return email.email
            except MultipleObjectsReturned:
                email = EmailAddress.objects.filter(user=person.user)
                if email.exists():
                    return email.email.first()
            except ObjectDoesNotExist:
                if person.user.email:
                    return person.user.email

    if person.profile_email:
        return person.profile_email
    else:
        return None


def get_email_object(person):
    try:
        user_object = person.user
    except:
        return None

    try:
        email_object, email_created = EmailAddress.objects.get_or_create(
                    user=user_object)
    except MultipleObjectsReturned:
        email_objects = EmailAddress.objects.filter(user=user_object)
        if email_objects.filter(verified=True).count() == 1:
            email_object = email_objects.get(verified=True)
        else:
            email_object = email_objects.first()
            for em in email_objects:
                if em != email_object:
                    em.delete()
        email_created = False

    return email_object, email_created


def email_verified(person):
    '''This method looks for a verified email and returns True if and only if
    1 verified email exists.'''

    if person.user:
        try:
            email = EmailAddress.objects.get(user=person.user, verified=True)
            return email.verified
        except ObjectDoesNotExist:
            try:
                email = EmailAddress.objects.get(user=person.user)
                return email.verified
            except MultipleObjectsReturned:
                return False
            except ObjectDoesNotExist:
                return False
    return False
