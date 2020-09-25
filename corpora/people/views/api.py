from django.utils.translation import ugettext_lazy as _
from people.models import \
    Person, Tribe, Demographic, KnownLanguage

from people.helpers import get_person
from rest_framework import viewsets, permissions
from rest_framework.views import APIView

from people.serializers import PersonSerializer,\
                         TribeSerializer, \
                         DemographicSerializer,\
                         KnownLanguageSerializer, \
                         MagicLoginSerializer

from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from corpora.email_utils import EMail
from django.contrib.sites.shortcuts import get_current_site

from django.core.signing import TimestampSigner, dumps


import logging
logger = logging.getLogger('corpora')


class DetailViewset(
  mixins.CreateModelMixin,
  mixins.RetrieveModelMixin,
  mixins.UpdateModelMixin,
  mixins.DestroyModelMixin,
  viewsets.GenericViewSet):
    pass


class StaffOnlyPermissions(permissions.BasePermission):
    """
    Model permission to only allow staff to view/edit model & objects.
    """

    def has_permission(self, request, view):
        return request.user.is_staff and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff and request.user.is_authenticated


class PersonPermissions(permissions.BasePermission):
    """
    Only a person can edit his/her own info. This
    involved all info including related models; therefore this persmission
    must work accross all the related hyperlink viewsets. Note that we
    don't require authentication to edit the person's info. This
    allows an anyone using the same device to provide info without
    having to create a login.
    """

    def has_permission(self, request, view):

        if request.user.is_staff and request.user.is_authenticated:
            self.message = _("Only staff can view this information.")
            return True
        elif request.method.lower() in 'post put':
            return True
        else:
            self.message = _("You're not allowed to view this information.")
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff and request.user.is_authenticated:
            # Authenticated staff have full access
            return True
        else:
            person = get_person(request)
            if person == obj:
                # Only a person can view/edit his/her own data
                if request.method in permissions.SAFE_METHODS:
                    # No authentication needed to view data
                    return True
                elif request.method in ['POST', 'PUT']:
                    return True  # No longer requiring authentication

                    # Authentication needed to edit data
                    self.message = _("You must sign in to edit your info.")
                    return request.user.is_authenticated
            else:
                self.message = _("You're not allowed to view this information.")
                return False
        self.message = _("You're not allowed to view this information.")
        return False


class PersonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Person to be viewed or edited.
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (PersonPermissions,)

    # def get_queryset(self):



class TribeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sentences to be viewed or edited.
    """

    queryset = Tribe.objects.all()
    serializer_class = TribeSerializer
    permission_classes = (PersonPermissions,)


class DemographicViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows recordings to be viewed or edited.
    """
    queryset = Demographic.objects.all()
    serializer_class = DemographicSerializer
    permission_classes = (PersonPermissions,)


class KnownLanguageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows recordings to be viewed or edited.
    """
    queryset = KnownLanguage.objects.all()
    serializer_class = KnownLanguageSerializer
    permission_classes = (PersonPermissions,)

    def get_queryset(self):
        person = get_person(self.request)
        return KnownLanguage.objects.filter(person=person)


class ProfilePermissions(PersonPermissions):
    """
    A special API endpoint to allow users to get their profile info.
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        person = get_person(request)
        if obj.id == person.id:
            return True
        return False


class ProfileViewSet(viewsets.ModelViewSet):
    """
    The /profile endpoint allows users to access their profiel information.

    `/profile/` will return a single result of the users information. This is
    a convienince method when a person's ID isn't known but you have their
    authentication credentials.

    `/profile/id` wille return the person object. This works when you have
    a person's id.
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (ProfilePermissions,)

    def get_queryset(self):
        person = get_person(self.request)
        queryset = Person.objects.filter(pk=person.pk)
        return queryset


class MagicLoginView(APIView):
    '''
    Post an email to this endpoint and a magic login link will
    be sent to that email if it exists
    '''

    def post(self, request, format=None):
        errors = {'error': 'You must post an email field.'}
        serializer = MagicLoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=request.data["email"])
                # request.user = user
                signer = TimestampSigner()
                payload = dumps({"email": user.email})
                value = signer.sign(payload)
                site = get_current_site(request)
                link = "https://{0}/magic/?key={1}".format(site.domain, value)
                email = EMail(to=user.email, subject='Login Link for {0}'.format(site.name), request=request)
                ctx = {'email': user.email, 'link': link, 'request': request, 'site': site}
                email.text('people/email/magiclogin.txt', ctx)
                email.html('people/email/magiclogin.html', ctx)  # Optional
                email.send()

                return Response(serializer.data, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                errors = {'error': 'Email does not exist.'}
                pass
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)





